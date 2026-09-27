import customtkinter as ctk

import network_monitor
import firewall_controller
import state_manager

REFRESH_INTERVAL_MS = 2000

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AppRow(ctk.CTkFrame):
    def __init__(self, master, app_name, connection_count, status, on_unblock=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.on_unblock = on_unblock

        self.label = ctk.CTkLabel(self, text=app_name, anchor="w")
        self.label.grid(row=0, column=0, sticky="ew", padx=8)

        self.conn_label = ctk.CTkLabel(
            self, text=f"{connection_count} اتصال", text_color="gray70"
        )
        self.conn_label.grid(row=0, column=1, padx=8)

        self.badge = ctk.CTkLabel(self, width=90, corner_radius=8)
        self.badge.grid(row=0, column=2, padx=8, pady=2)

        self.unblock_btn = None
        if status == "blocked" and self.on_unblock:
            self.unblock_btn = ctk.CTkButton(
                self, text="فك الحظر", width=70, height=24,
                fg_color="#d97706", hover_color="#b45309",
                command=lambda: self.on_unblock(app_name)
            )
            self.unblock_btn.grid(row=0, column=3, padx=4)

        self.update_row(connection_count, status)

    def update_row(self, connection_count, status):
        self.conn_label.configure(text=f"{connection_count} اتصال")

        badge_config = {
            "priority": {"text": " أولوية", "fg": "#2fa572", "text_color": "white"},
            "blocked": {"text": " محظور", "fg": "#c0392b", "text_color": "white"},
            "normal": {"text": "عادي", "fg": "gray30", "text_color": "gray90"},
        }.get(status, {"text": "عادي", "fg": "gray30", "text_color": "gray90"})

        self.badge.configure(
            text=badge_config["text"],
            fg_color=badge_config["fg"],
            text_color=badge_config["text_color"]
        )


class NetPriorityApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NetPriority — إدارة أولوية الإنترنت")
        self.geometry("560x640")
        self.minsize(480, 500)

        self.priority_mode_active = False
        self.selected_priority_app = ctk.StringVar(value="")
        self.blocked_apps = set(state_manager.get_blocked_apps())
        
        self.app_rows = {}

        self._build_layout()
        self._check_admin_and_leftovers()
        self._refresh_loop()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self):
        header = ctk.CTkLabel(
            self, text="🌐 NetPriority",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        header.pack(pady=(16, 4))

        self.status_label = ctk.CTkLabel(
            self, text="جاري فحص التطبيقات...", text_color="gray70"
        )
        self.status_label.pack(pady=(0, 10))

        picker_frame = ctk.CTkFrame(self)
        picker_frame.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(picker_frame, text="تطبيق الأولوية:").pack(
            side="right", padx=8, pady=8
        )
        self.priority_menu = ctk.CTkOptionMenu(
            picker_frame, variable=self.selected_priority_app,
            values=["-- اختر تطبيق --"],
        )
        self.priority_menu.pack(side="right", padx=8, pady=8, fill="x", expand=True)

        self.list_frame = ctk.CTkScrollableFrame(self, label_text="التطبيقات النشطة")
        self.list_frame.pack(fill="both", expand=True, padx=16, pady=8)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(4, 16))

        self.activate_btn = ctk.CTkButton(
            btn_frame, text=" تفعيل وضع الأولوية",
            command=self._on_activate, fg_color="#2fa572", hover_color="#248a5c",
        )
        self.activate_btn.pack(side="right", padx=4, expand=True, fill="x")

        self.reset_btn = ctk.CTkButton(
            btn_frame, text=" إعادة ضبط الكل",
            command=self._on_reset, fg_color="#c0392b", hover_color="#992d22",
        )
        self.reset_btn.pack(side="right", padx=4, expand=True, fill="x")

    def _check_admin_and_leftovers(self):
        if not firewall_controller.is_admin():
            self.status_label.configure(
                text=" شغّل البرنامج كـ Administrator عشان يقدر يتحكم بالجدار الناري",
                text_color="#e67e22",
            )
            self.activate_btn.configure(state="disabled")
            return

        if state_manager.has_leftover_blocks():
            leftover = state_manager.get_blocked_apps()
            firewall_controller.unblock_all(leftover)
            state_manager.clear_state()
            self.blocked_apps = set()
            self.status_label.configure(
                text=f"تم تنظيف {len(leftover)} حظر عالق من تشغيل سابق ",
                text_color="#2fa572",
            )

    def _refresh_loop(self):
        apps = network_monitor.get_active_apps()
        playable = network_monitor.get_playable_apps(apps)
        self._render_app_list(playable)
        self.after(REFRESH_INTERVAL_MS, self._refresh_loop)

    def _render_app_list(self, apps):
        current_names = sorted(apps.keys(), key=lambda n: n.lower())
        menu_values = current_names if current_names else ["لا توجد تطبيقات نشطة"]
        
        if list(self.priority_menu._values) != menu_values:
            self.priority_menu.configure(values=menu_values)

        if not current_names:
            for row in self.app_rows.values():
                row.destroy()
            self.app_rows.clear()
            
            if not hasattr(self, "no_apps_label") or not self.no_apps_label.winfo_exists():
                self.no_apps_label = ctk.CTkLabel(self.list_frame, text="ما فيه تطبيقات تستخدم النت حاليًا")
                self.no_apps_label.pack(pady=20)
            return
        else:
            if hasattr(self, "no_apps_label") and self.no_apps_label.winfo_exists():
                self.no_apps_label.destroy()

        priority_name = self.selected_priority_app.get()
        active_names_set = set(current_names)

        dead_apps = [name for name in self.app_rows if name not in active_names_set]
        for name in dead_apps:
            self.app_rows[name].destroy()
            del self.app_rows[name]

        for name in current_names:
            info = apps[name]
            if self.priority_mode_active and name == priority_name:
                status = "priority"
            elif name in self.blocked_apps:
                status = "blocked"
            else:
                status = "normal"

            if name in self.app_rows:
                row = self.app_rows[name]
                if hasattr(row, 'last_status') and row.last_status != status:
                    row.destroy()
                    row = AppRow(self.list_frame, name, info.connection_count, status, on_unblock=self._on_unblock_single_app)
                    row.pack(fill="x", pady=2)
                    row.last_status = status
                    self.app_rows[name] = row
                else:
                    row.update_row(info.connection_count, status)
            else:
                row = AppRow(self.list_frame, name, info.connection_count, status, on_unblock=self._on_unblock_single_app)
                row.pack(fill="x", pady=2)
                row.last_status = status
                self.app_rows[name] = row

        for name in current_names:
            if name in self.app_rows:
                self.app_rows[name].pack_forget()
                self.app_rows[name].pack(fill="x", pady=2)

        if not self.priority_mode_active:
            self.status_label.configure(
                text=f"{len(current_names)} تطبيق نشط — وضع الأولوية متوقف",
                text_color="gray70",
            )

    def _on_activate(self):
        priority_name = self.selected_priority_app.get()
        if not priority_name or priority_name.startswith("--") or priority_name.startswith("لا توجد"):
            self.status_label.configure(text="اختر تطبيق أولوية أولاً", text_color="#e67e22")
            return

        apps = network_monitor.get_playable_apps(network_monitor.get_active_apps())
        blocked_count = 0
        for name, info in apps.items():
            if name == priority_name:
                continue
            if firewall_controller.block_app(name, info.exe_path):
                self.blocked_apps.add(name)
                state_manager.add_blocked_app(name)
                blocked_count += 1

        self.priority_mode_active = True
        self.status_label.configure(
            text=f" وضع الأولوية شغّال — تم حظر {blocked_count} تطبيق مؤقتًا",
            text_color="#2fa572",
        )

    def _on_unblock_single_app(self, app_name):
        firewall_controller.unblock_app(app_name)
        if app_name in self.blocked_apps:
            self.blocked_apps.remove(app_name)
            state_manager.remove_blocked_app(app_name)
        
        self.status_label.configure(
            text=f"تم فك الحظر عن التطبيق: {app_name} بنجاح ",
            text_color="#2fa572",
        )

    def _on_reset(self, clear_priority=True):
        firewall_controller.unblock_all(list(self.blocked_apps))
        self.blocked_apps = set()
        state_manager.clear_state()
        self.priority_mode_active = False
        if clear_priority:
            self.selected_priority_app.set("-- اختر تطبيق --")
        self.status_label.configure(text="تم رجوع كل شي طبيعي ", text_color="gray70")

    def _on_close(self):
        if self.blocked_apps:
            firewall_controller.unblock_all(list(self.blocked_apps))
            state_manager.clear_state()
        self.destroy()