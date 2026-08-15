import flet as ft
from typing import Callable
from src.domain.models import CompanySettings
from src.services.config import ConfigService, AppConfig

class SettingsViewComponent(ft.Container):
    def __init__(self, company_settings: CompanySettings, config_service: ConfigService, on_save_callback: Callable):
        self.company_settings = company_settings
        self.config_service = config_service
        self.on_save_callback = on_save_callback

        # 1. Company Profile Fields
        self.txt_name = ft.TextField(label="Company Name", value=self.company_settings.company_name, dense=True, expand=2)
        self.txt_phone = ft.TextField(label="Phone", value=self.company_settings.phone, dense=True, expand=1)
        self.txt_email = ft.TextField(label="Email", value=self.company_settings.email, dense=True, expand=1)
        self.txt_website = ft.TextField(label="Website", value=self.company_settings.website, dense=True, expand=1)
        self.txt_state = ft.TextField(label="State", value=self.company_settings.state, dense=True, expand=2)
        self.txt_state_code = ft.TextField(label="State Code", value=self.company_settings.state_code, dense=True, expand=1)
        self.txt_address = ft.TextField(
            label="Company Address",
            value=self.company_settings.address,
            multiline=True,
            min_lines=2,
            max_lines=3,
            dense=True,
            expand=True,
        )

        # 2. Tax Identifiers
        self.txt_gstin = ft.TextField(label="GSTIN", value=self.company_settings.gstin, dense=True, expand=1)
        self.txt_pan = ft.TextField(label="PAN", value=self.company_settings.pan, dense=True, expand=1)

        # 3. Bank Details
        self.txt_bank_name = ft.TextField(label="Bank Name", value=self.company_settings.bank_name, dense=True, expand=1)
        self.txt_acc_no = ft.TextField(label="Account Number", value=self.company_settings.account_number, dense=True, expand=1)
        self.txt_branch = ft.TextField(label="Branch", value=self.company_settings.branch, dense=True, expand=1)
        self.txt_ifsc = ft.TextField(label="IFSC Code", value=self.company_settings.ifsc, dense=True, expand=1)

        # 4. Legal & Signatory
        self.txt_declaration = ft.TextField(
            label="Invoice Declaration Text",
            value=self.company_settings.declaration,
            multiline=True,
            min_lines=2,
            max_lines=3,
            dense=True,
            expand=True,
        )
        self.txt_signatory = ft.TextField(label="Authorised Signatory Title", value=self.company_settings.authorised_signatory, dense=True, expand=1)

        # 5. Storage Locations
        app_cfg = self.config_service.config
        self.txt_db_dir = ft.TextField(label="SQLite Database Directory", value=app_cfg.db_directory, dense=True, expand=True)
        self.txt_pdf_dir = ft.TextField(label="Default PDF Invoices Directory", value=app_cfg.pdf_export_directory, dense=True, expand=True)

        self.txt_status = ft.Text("", size=12, color=ft.Colors.GREEN_800, weight=ft.FontWeight.BOLD)

        btn_save = ft.FilledButton(
            "Save All Settings",
            icon=ft.Icons.SAVE,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_800,
                color=ft.Colors.WHITE,
            ),
            on_click=lambda _: self._save_settings(),
        )

        btn_reset = ft.OutlinedButton(
            "Reset to Defaults",
            icon=ft.Icons.RESTORE,
            on_click=lambda _: self._reset_defaults(),
        )

        super().__init__(
            content=ft.Column(
                controls=[
                    # Header
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.SETTINGS, size=28, color=ft.Colors.BLUE_800),
                            ft.Text("Company Profile, Tax & Storage Settings", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_300),

                    # 1. Profile Section
                    self._create_section_card(
                        "1. Company Profile & Contact",
                        [
                            ft.Row([self.txt_name, self.txt_phone]),
                            ft.Row([self.txt_email, self.txt_website]),
                            ft.Row([self.txt_state, self.txt_state_code]),
                            ft.Row([self.txt_address]),
                        ]
                    ),

                    # 2. Tax IDs
                    self._create_section_card(
                        "2. Tax Identifiers",
                        [
                            ft.Row([self.txt_gstin, self.txt_pan]),
                        ]
                    ),

                    # 3. Bank & Payment
                    self._create_section_card(
                        "3. Bank & Payment Details (for NEFT / RTGS)",
                        [
                            ft.Row([self.txt_bank_name, self.txt_acc_no]),
                            ft.Row([self.txt_branch, self.txt_ifsc]),
                        ]
                    ),

                    # 4. Legal & Signatory
                    self._create_section_card(
                        "4. Declaration & Signatory",
                        [
                            ft.Row([self.txt_declaration]),
                            ft.Row([self.txt_signatory]),
                        ]
                    ),

                    # 5. Storage Directories
                    self._create_section_card(
                        "5. Storage & File Locations (User Configured)",
                        [
                            ft.Text("Define where SQLite database files and exported PDF invoices are stored outside of the app package:", size=11, color=ft.Colors.GREY_700),
                            ft.Row([self.txt_db_dir]),
                            ft.Row([self.txt_pdf_dir]),
                        ]
                    ),

                    # Action bar
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.txt_status,
                                ft.Row([btn_reset, btn_save], spacing=10),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.Padding.symmetric(vertical=10),
                    )
                ],
                spacing=14,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.Padding.all(16),
            expand=True,
        )

    def _create_section_card(self, title: str, controls: list) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.BLUE_800),
                    *controls
                ],
                spacing=8,
            ),
            padding=ft.Padding.all(12),
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
        )

    def _save_settings(self):
        try:
            name = self.txt_name.value.strip()
            address = self.txt_address.value.strip()
            gstin = self.txt_gstin.value.strip()
            pan = self.txt_pan.value.strip()
            state = self.txt_state.value.strip()
            state_code = self.txt_state_code.value.strip()
            bank_name = self.txt_bank_name.value.strip()
            acc_no = self.txt_acc_no.value.strip()
            ifsc = self.txt_ifsc.value.strip()
            db_dir = self.txt_db_dir.value.strip()
            pdf_dir = self.txt_pdf_dir.value.strip()

            if not name:
                self.set_status("Please enter a valid Company Name.", is_error=True)
                return
            if not address:
                self.set_status("Please enter a valid Company Address.", is_error=True)
                return
            if not gstin:
                self.set_status("Please enter a valid GSTIN.", is_error=True)
                return
            if not pan:
                self.set_status("Please enter a valid PAN.", is_error=True)
                return
            if not db_dir or not pdf_dir:
                self.set_status("Please specify valid storage directory paths.", is_error=True)
                return

            # Update Company Settings model
            updated_settings = CompanySettings(
                company_name=name,
                address=address,
                gstin=gstin,
                pan=pan,
                state=state,
                state_code=state_code,
                phone=self.txt_phone.value.strip(),
                email=self.txt_email.value.strip(),
                website=self.txt_website.value.strip(),
                bank_name=bank_name,
                account_number=acc_no,
                branch=self.txt_branch.value.strip(),
                ifsc=ifsc,
                declaration=self.txt_declaration.value.strip(),
                authorised_signatory=self.txt_signatory.value.strip(),
            )

            # Update App Config
            new_config = AppConfig(
                db_directory=db_dir,
                pdf_export_directory=pdf_dir,
                is_configured=True,
            )
            self.config_service.save_config(new_config)

            self.on_save_callback(updated_settings, new_config)
            self.set_status("Settings & Storage Locations saved successfully!")
        except Exception as e:
            self.set_status(f"Error saving settings: {e}", is_error=True)

    def _reset_defaults(self):
        defaults = CompanySettings()
        self.txt_name.value = defaults.company_name
        self.txt_address.value = defaults.address
        self.txt_gstin.value = defaults.gstin
        self.txt_pan.value = defaults.pan
        self.txt_state.value = defaults.state
        self.txt_state_code.value = defaults.state_code
        self.txt_phone.value = defaults.phone
        self.txt_email.value = defaults.email
        self.txt_website.value = defaults.website
        self.txt_bank_name.value = defaults.bank_name
        self.txt_acc_no.value = defaults.account_number
        self.txt_branch.value = defaults.branch
        self.txt_ifsc.value = defaults.ifsc
        self.txt_declaration.value = defaults.declaration
        self.txt_signatory.value = defaults.authorised_signatory
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass
        self.set_status("Fields reset to defaults. Click 'Save All Settings' to apply.")

    def set_status(self, message: str, is_error: bool = False):
        self.txt_status.value = message
        self.txt_status.color = ft.Colors.RED_700 if is_error else ft.Colors.GREEN_800
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass
