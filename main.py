import subprocess
import json
import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio


class RDPServ:
    def __init__(self):
        self.name: str = "server name"
        self.address: str = "example.com"
        self.port: int = 3389
        self.user: str = "user"
        self.pwd: str = ""
        self.width: int = 1920
        self.height: int = 1080

    def get_liststore_item(self) -> (str, str):
        return self.name, f"{self.address}:{self.port}"

    def get_command(self) -> tuple[str, str, str, str, str, str]:
        return ("xfreerdp", f"/v:{self.address}", f"/port:{self.port}", f"/u:{self.user}",
                f"/p:{self.pwd}", f"/size:{self.width}x{self.height}")

    def set_from_dict(self, data: dict):
        name = data.get("name")
        if name:
            self.name = name
        address = data.get("address")
        if address:
            self.address = address
        port = data.get("port")
        if port is not None:
            self.port = port
        user = data.get("user")
        if user:
            self.user = user
        pwd = data.get("pwd")
        if pwd:
            self.pwd = pwd
        width = data.get("width")
        if width is not None:
            self.width = width
        height = data.get("height")
        if height is not None:
            self.height = height

    def get_dict(self):
        return {
            "name": self.name,
            "address": self.address,
            "port": self.port,
            "user": self.user,
            "pwd": self.pwd,
            "width": self.width,
            "height": self.height
        }

class MainApplication(Gtk.Application):
    def __init__(self, *args, **kargs):
        super().__init__(
            *args,
            application_id="org.example.freerdp-pygui",
            **kargs
        )
        self.connect("activate", self.on_activate)

    def on_activate(self, app: Gtk.Application):
        window = MainWindow(app)
        window.show_all()


class ServEditWindow(Gtk.Window):
    def __init__(self, title: str, serv: RDPServ):
        self.confirmed = False
        self.edited_serv = RDPServ()

        super().__init__(title=title)
        self.set_resizable(False)

        # grid layout
        self.grid = Gtk.Grid()
        self.add(self.grid)

        # labels
        name_label = Gtk.Label(label="Name:")
        host_label = Gtk.Label(label="Host:")
        port_label = Gtk.Label(label="Port:")
        user_label = Gtk.Label(label="User:")
        pwd_label = Gtk.Label(label="Password:")
        screensize_label = Gtk.Label(label="Screen Size:")
        x_label = Gtk.Label(label=" x ")

        # entries
        self.name_entry = Gtk.Entry()
        self.host_entry = Gtk.Entry()
        self.port_entry = Gtk.Entry()
        self.user_entry = Gtk.Entry()
        self.pwd_entry = Gtk.Entry()
        self.width_entry = Gtk.Entry()
        self.height_entry = Gtk.Entry()
        self.pwd_entry.set_visibility(False)

        # buttons
        self.confirm_button = Gtk.Button(label="Confirm")
        self.cancel_button = Gtk.Button(label="Cancel")
        # signals
        self.confirm_button.connect("clicked", self.on_confirm_button_clicked)
        self.cancel_button.connect("clicked", self.on_cancel_button_clicked)

        # add to grid layout
        self.grid.attach(name_label,       0, 0, 1, 1)
        self.grid.attach(host_label,       0, 1, 1, 1)
        self.grid.attach(port_label,       0, 2, 1, 1)
        self.grid.attach(user_label,       0, 3, 1, 1)
        self.grid.attach(pwd_label,        0, 4, 1, 1)
        self.grid.attach(screensize_label, 0, 5, 1, 1)

        self.grid.attach(self.name_entry, 1, 0, 3, 1)
        self.grid.attach(self.host_entry, 1, 1, 3, 1)
        self.grid.attach(self.port_entry, 1, 2, 3, 1)
        self.grid.attach(self.user_entry, 1, 3, 3, 1)
        self.grid.attach(self.pwd_entry,  1, 4, 3, 1)

        self.grid.attach(self.width_entry,  1, 5, 1, 1)
        self.grid.attach(x_label,           2, 5, 1, 1)
        self.grid.attach(self.height_entry, 3, 5, 1, 1)

        self.grid.attach(self.confirm_button, 1, 6, 1, 1)
        self.grid.attach(self.cancel_button,  3, 6, 1, 1)

        # set entry text
        self.name_entry.set_text(serv.name)
        self.host_entry.set_text(serv.address)
        self.port_entry.set_text(str(serv.port))
        self.user_entry.set_text(serv.user)
        self.pwd_entry.set_text(serv.pwd)
        self.width_entry.set_text(str(serv.width))
        self.height_entry.set_text(str(serv.height))

    def on_cancel_button_clicked(self, button: Gtk.Button):
        self.destroy()

    def on_confirm_button_clicked(self, button: Gtk.Button):
        try:
            self.edited_serv.name = self.name_entry.get_text()
            self.edited_serv.address = self.host_entry.get_text()
            self.edited_serv.port = int(self.port_entry.get_text())
            self.edited_serv.user = self.user_entry.get_text()
            self.edited_serv.pwd = self.pwd_entry.get_text()
            self.edited_serv.width = int(self.width_entry.get_text())
            self.edited_serv.height = int(self.height_entry.get_text())

            if not(
                len(self.edited_serv.name) and len(self.edited_serv.address) and
                len(self.edited_serv.user) and len(self.edited_serv.pwd)
            ):
                msg_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Error"
                )
                msg_dialog.format_secondary_text("No Empty.")
                msg_dialog.run()
                msg_dialog.destroy()
                return
        except:
            msg_dialog = Gtk.MessageDialog(
                transient_for = self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error"
            )
            msg_dialog.format_secondary_text("Port or Width or Height must be a intager.")
            msg_dialog.run()
            msg_dialog.destroy()
            return

        self.confirmed = True
        self.destroy()


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application):
        # server list, type: RDPServ
        self.serv_list: list[RDPServ] = list()
        self.load_servers()

        super().__init__(title="RDP Servers", application=app)
        # window size
        self.set_default_size(800, 400)

        # header bar
        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)
        self.hb.props.title = "RDP Servers"
        self.set_titlebar(self.hb)

        # add_button with icon
        self.add_button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-new-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.add_button.add(image)

        # add add_button to header bar
        self.hb.pack_start(self.add_button)

        # model
        self.serv_liststore = Gtk.ListStore(str, str)
        self.set_liststore_from_serv_list()

        # view
        self.treeview = Gtk.TreeView(model=self.serv_liststore)

        # name column
        renderer_serv_name = Gtk.CellRendererText()
        renderer_serv_name.set_fixed_size(200, 50)
        column_text_serv_name = Gtk.TreeViewColumn("Name", renderer_serv_name, text=0)
        self.treeview.append_column(column_text_serv_name)

        # server address column
        renderer_serv_addr = Gtk.CellRendererText()
        renderer_serv_addr.set_fixed_size(600, 50)
        column_text_serv_addr = Gtk.TreeViewColumn("Address", renderer_serv_addr, text=1)
        self.treeview.append_column(column_text_serv_addr)

        # menu
        self.menu = Gtk.Menu()
        # Edit menu item
        edit_menuitem = Gtk.MenuItem(label="Edit")
        self.menu.append(edit_menuitem)
        # Delete menu item
        del_menuitem = Gtk.MenuItem(label="Delete")
        self.menu.append(del_menuitem)
        self.menu.show_all()

        # signals
        self.add_button.connect("clicked", self.on_new_button_press)
        self.treeview.connect("row-activated", self.on_treeview_row_activated)
        self.treeview.connect("button-press-event", self.on_treeview_button_press)
        edit_menuitem.connect("activate", self.on_edit_menuitem_activate)
        del_menuitem.connect("activate", self.on_del_menuitem_activate)

        # add treeview to main window
        self.add(self.treeview)

    def set_liststore_from_serv_list(self):
        self.serv_liststore.clear()
        for serv in self.serv_list:
            self.serv_liststore.append(serv.get_liststore_item())

    def on_treeview_row_activated(self, treeview: Gtk.TreeView, path: Gtk.TreePath, column: Gtk.TreeViewColumn):
        index = path.get_indices()[0]
        # self.close()
        subprocess.Popen(self.serv_list[index].get_command())
        # exit(0)

    def on_treeview_button_press(self, treeview: Gtk.TreeView, event: Gdk.EventButton):
        # right click
        if event.button == 3:
            try:
                path, column, _, _ = treeview.get_path_at_pos(int(event.x), int(event.y))
                self.menu.popup(None, None, None, None, event.button, event.time)
            except:
                pass

    def on_new_button_press(self, button: Gtk.Button):
        new_serv = RDPServ()
        new_serv_edit_window = ServEditWindow(title="new", serv=new_serv)
        new_serv_edit_window.connect("destroy", self.on_new_edit_window_destroy)
        new_serv_edit_window.show_all()

    def on_new_edit_window_destroy(self, serv_edit_window: ServEditWindow):
        if serv_edit_window.confirmed:
            self.serv_list.append(serv_edit_window.edited_serv)
            self.serv_liststore.append(serv_edit_window.edited_serv.get_liststore_item())
            self.save_servers()

    def on_edit_menuitem_activate(self, menuitem: Gtk.MenuItem):
        path, column = self.treeview.get_cursor()
        index = path.get_indices()[0]
        serv = self.serv_list[index]
        serv_edit_window = ServEditWindow(title="Edit", serv=serv)
        serv_edit_window.connect("destroy", self.on_edit_window_destroy, index)
        serv_edit_window.show_all()

    def on_edit_window_destroy(self, serv_edit_window: ServEditWindow, index: int):
        if serv_edit_window.confirmed:
            self.serv_list[index] = serv_edit_window.edited_serv
            self.save_servers()
            self.set_liststore_from_serv_list()

    def on_del_menuitem_activate(self, menuitem: Gtk.MenuItem):
        path, column = self.treeview.get_cursor()
        index = path.get_indices()[0]
        self.serv_list.pop(index)
        self.save_servers()
        self.set_liststore_from_serv_list()

    def load_servers(self):
        if os.path.exists('serv.json'):
            with open('serv.json', 'r', encoding='utf-8') as fp:
                servs_dict = json.load(fp)
                for serv_dict in servs_dict:
                    serv = RDPServ()
                    serv.set_from_dict(serv_dict)
                    self.serv_list.append(serv)

    def save_servers(self):
        servs_dict = [serv.get_dict() for serv in self.serv_list]
        if os.path.exists('serv.json'):
            os.remove('serv.json')
        with open('serv.json', 'w', encoding='utf-8') as fp:
            json.dump(servs_dict, fp)


if __name__ == "__main__":
    app = MainApplication()
    app.run(None)
