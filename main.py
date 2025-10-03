# truss_input.py
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from visualizer import TrussVisualizer
import truss

class TrussInput:
    def __init__(self, root):
        self.root = root
        self.root.title("Truss Input")
        self.root.geometry("1400x800")
        self.root.configure(bg="#f0f0f0")

        self.visualizer = TrussVisualizer(root)
        self.visualizer.canvas.bind("<Button-1>", self.on_canvas_click)

        self.joints = {}
        self.members = []
        self.loads = {}
        self.supports = {}
        self.click_selection = []

        self.adding_load = False
        self.setting_support = False
        self.deleting = False

        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.control_frame = ttk.Frame(self.main_frame, width=200, padding="10", relief="solid", borderwidth=2)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.canvas_frame = ttk.Frame(self.main_frame, padding="10")
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.add_button("Add Joint", self.add_joint, self.control_frame)
        self.add_button("Add Load", self.add_load, self.control_frame)
        self.add_button("Set Support", self.set_support, self.control_frame)
        self.add_button("Solve Truss", self.solve_truss, self.control_frame)
        self.add_button("Delete", self.delete_element, self.control_frame)
        self.add_button("Reset", self.reset_all, self.control_frame)

        self.info_label = ttk.Label(self.control_frame, text="Tip: Click two joints to\n add a member.", anchor="w", width=20)
        self.info_label.pack(side=tk.BOTTOM, padx=5, pady=5)

        self.support_reactions_label = ttk.Label(self.control_frame, text="", anchor="w", width=40, justify="left")
        self.support_reactions_label.pack(side=tk.BOTTOM, padx=5, pady=10)

        self.visualizer.canvas.pack(fill=tk.BOTH, expand=True)

    def add_button(self, text, command, parent_frame):
        button = ttk.Button(parent_frame, text=text, command=command, width=20, padding="5")
        button.config(style="TButton")
        button.pack(pady=5)

    def on_canvas_click(self, event):
        if self.deleting:
            self.try_delete_element(event.x, event.y)
            return

        clicked_joint = self.visualizer.find_nearest_joint(event.x, event.y)
        if clicked_joint:
            if self.adding_load:
                self.add_load_to_joint(clicked_joint)
            elif self.setting_support:
                self.set_support_for_joint(clicked_joint)
            elif len(self.click_selection) < 2:
                self.click_selection.append(clicked_joint)
                if len(self.click_selection) == 2:
                    j1, j2 = self.click_selection
                    if j1 != j2 and (j1, j2) not in self.members and (j2, j1) not in self.members:
                        self.members.append((j1, j2))
                        self.visualizer.members.append((j1, j2))
                        self.visualizer.update_plot()
                    self.click_selection.clear()

    def add_joint(self):
        joint_name = simpledialog.askstring("Input", "Enter joint name:")
        x = simpledialog.askfloat("Input", "Enter X coordinate:")
        y = simpledialog.askfloat("Input", "Enter Y coordinate:")
        if joint_name and x is not None and y is not None:
            self.joints[joint_name] = (x, y)
            self.visualizer.joints[joint_name] = (x, y)
            self.visualizer.update_plot()

    def add_load(self):
        if not self.joints:
            messagebox.showwarning("Warning", "No joints available to apply a load.")
            return
        self.adding_load = True
        self.setting_support = False
        self.info_label.config(text="Click on a joint to apply \na load.")

    def add_load_to_joint(self, joint_name):
        fx = simpledialog.askfloat("Input", f"Enter X direction force at joint {joint_name}:")
        fy = simpledialog.askfloat("Input", f"Enter Y direction force at joint {joint_name}:")
        if fx is not None and fy is not None:
            ext = "Ext_" + joint_name
            self.loads[ext] = [fx, fy]
            self.visualizer.loads.append((joint_name, fx, fy))
            self.visualizer.update_plot()
            self.adding_load = False
            self.info_label.config(text="Tip: Click two joints to add \na member.")

    def set_support(self):
        if not self.joints:
            messagebox.showwarning("Warning", "No joints available to set support.")
            return
        self.setting_support = True
        self.adding_load = False
        self.info_label.config(text="Click on a joint to set support.")

    def set_support_for_joint(self, joint_name):
        fix_x = messagebox.askyesno("Support", f"Fix X direction at {joint_name}?")
        fix_y = messagebox.askyesno("Support", f"Fix Y direction at {joint_name}?")
        self.supports[joint_name] = [fix_x, fix_y]
        self.visualizer.supports.append((joint_name, fix_x, fix_y))
        self.visualizer.update_plot()
        self.setting_support = False
        self.info_label.config(text="Tip: Click two joints to add \na member.")

    def solve_truss(self):
        if not self.joints or not self.members:
            messagebox.showwarning("Warning", "Truss is incomplete! Add joints and members first.")
            return
        try:
            member_forces, support_reactions = truss.solve(
                self.joints, self.members, self.loads, self.supports
            )
            self.visualizer.update_member_colors(member_forces)
            result_text = "Support Reactions:\n"
            for support, reaction in support_reactions.items():
                rx = float(reaction[0])
                ry = float(reaction[1])
                result_text += f"{support}: ({rx:.2f}, {ry:.2f}) N\n"
            result_text += "\nColors:\nRED = COMPRESSION\nGREEN = TENSION\nYELLOW = ZERO FORCE\n"
            self.support_reactions_label.config(text=result_text)
        except Exception:
            messagebox.showerror("Error", "Truss solution failed: Statically Indeterminate Truss")

    def reset_all(self):
        self.joints.clear()
        self.members.clear()
        self.loads.clear()
        self.supports.clear()
        self.click_selection.clear()
        self.adding_load = False
        self.setting_support = False
        self.visualizer.joints.clear()
        self.visualizer.members.clear()
        self.visualizer.loads.clear()
        self.visualizer.supports.clear()
        self.visualizer.member_lines.clear()
        self.visualizer.update_plot()
        self.support_reactions_label.config(text="")
        self.info_label.config(text="Tip: Click two joints to\n add a member.")

    def delete_element(self):
        self.deleting = True
        self.adding_load = False
        self.setting_support = False
        self.info_label.config(text="Click on a joint/member/\nload/support to delete it.")

    def try_delete_element(self, x, y):
        joint = self.visualizer.find_nearest_joint(x, y)
        if joint:
            self.joints.pop(joint, None)
            self.visualizer.joints.pop(joint, None)
            self.loads.pop("Ext_" + joint, None)
            self.supports.pop(joint, None)
            self.visualizer.loads = [l for l in self.visualizer.loads if l[0] != joint]
            self.visualizer.supports = [s for s in self.visualizer.supports if s[0] != joint]
            self.members = [m for m in self.members if joint not in m]
            self.visualizer.members = [m for m in self.visualizer.members if joint not in m]
            self.visualizer.update_plot()
            return

        for m in self.visualizer.members:
            j1, j2 = m
            x1, y1 = self.visualizer.joints[j1]
            x2, y2 = self.visualizer.joints[j2]
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            sx = cx * self.visualizer.grid_spacing + self.visualizer.offset_x
            sy = self.visualizer.offset_y - cy * self.visualizer.grid_spacing
            if abs(x - sx) < 10 and abs(y - sy) < 10:
                self.members.remove(m)
                self.visualizer.members.remove(m)
                self.visualizer.update_plot()
                return

        for l in list(self.visualizer.loads):
            j, fx, fy = l
            xj, yj = self.visualizer.joints[j]
            sx = xj * self.visualizer.grid_spacing + self.visualizer.offset_x
            sy = self.visualizer.offset_y - yj * self.visualizer.grid_spacing
            if abs(x - sx) < 10 and abs(y - sy) < 10:
                self.visualizer.loads.remove(l)
                self.loads.pop("Ext_" + j, None)
                self.visualizer.update_plot()
                return

        for s in list(self.visualizer.supports):
            j, fx, fy = s
            xj, yj = self.visualizer.joints[j]
            sx = xj * self.visualizer.grid_spacing + self.visualizer.offset_x
            sy = self.visualizer.offset_y - yj * self.visualizer.grid_spacing
            if abs(x - sx) < 10 and abs(y - sy) < 10:
                self.visualizer.supports.remove(s)
                self.supports.pop(j, None)
                self.visualizer.update_plot()
                return

        self.deleting = False
        self.info_label.config(text="Tip: Click two joints to add a member.")


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 12, "bold"), padding=10, width=20)
    app = TrussInput(root)
    root.mainloop()
