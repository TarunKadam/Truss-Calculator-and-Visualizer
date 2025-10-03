import tkinter as tk
import math

class TrussVisualizer:
    def __init__(self, root):
        self.root = root
        self.grid_spacing = 50
        self.offset_x = 50
        self.offset_y = 650
        self.joints = {}
        self.members = []
        self.loads = []
        self.supports = []
        self.member_lines = {}
        self.current_member_forces = {}
        self.show_forces = True
        self.force_text_ids = []

        self.canvas = tk.Canvas(root, width=1100, height=800, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.root.bind("<f>", self.toggle_forces)

        self.root.after(100, self.update_plot)

    def toggle_forces(self, event):
        self.show_forces = not self.show_forces
        self.update_plot()

    def draw_grid(self):
        self.canvas.delete("grid")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        spacing = self.grid_spacing

        for x in range(self.offset_x % spacing, width, spacing):
            self.canvas.create_line(x, 0, x, height, fill="#ddd", tags="grid")
        for y in range(self.offset_y % spacing, height, spacing):
            self.canvas.create_line(0, y, width, y, fill="#ddd", tags="grid")

        self.canvas.create_line(0, self.offset_y, width, self.offset_y, fill="black", width=1, tags="grid")
        self.canvas.create_line(self.offset_x, 0, self.offset_x, height, fill="black", width=1, tags="grid")

    def update_plot(self):
        self.canvas.delete("all")
        self.draw_grid()

        scale = self.grid_spacing
        ox = self.offset_x
        oy = self.offset_y

        for j1, j2 in self.members:
            if j1 in self.joints and j2 in self.joints:
                x1, y1 = self.joints[j1]
                x2, y2 = self.joints[j2]
                line_id = self.canvas.create_line(
                    x1 * scale + ox, oy - y1 * scale,
                    x2 * scale + ox, oy - y2 * scale,
                    fill="black", width=2
                )
                self.member_lines[tuple(sorted((j1, j2)))] = line_id

        for joint, (x, y) in self.joints.items():
            cx, cy = x * scale + ox, oy - y * scale
            self.canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill="blue")
            self.canvas.create_text(cx + 10, cy, text=joint, font=("Arial", 14, "bold"), fill="black")

        for joint, fx, fy in self.loads:
            if joint in self.joints:
                x, y = self.joints[joint]
                cx, cy = x * scale + ox, oy - y * scale
                if fx or fy:
                    angle = math.atan2(-fy, fx)
                    length = 25
                    end_x = cx + length * math.cos(angle)
                    end_y = cy + length * math.sin(angle)
                    self.canvas.create_line(cx, cy, end_x, end_y, arrow=tk.LAST, fill="red", width=3)
                    magnitude = math.sqrt(fx ** 2 + fy ** 2)
                    self.canvas.create_text(end_x + 12, end_y + 12, text=f"{magnitude:.2f}N", font=("Arial", 12, "bold"), fill="blue")

        for joint, fix_x, fix_y in self.supports:
            if joint in self.joints:
                x, y = self.joints[joint]
                cx, cy = x * scale + ox, oy - y * scale
                if fix_x and fix_y:
                    self.canvas.create_polygon(cx - 6, cy + 6, cx + 6, cy + 6, cx, cy - 6, fill="green")
                elif fix_y:
                    self.canvas.create_polygon(cx - 6, cy, cx + 6, cy, cx, cy + 6, fill="green")

        self.update_member_colors(self.current_member_forces)

    def update_member_colors(self, member_forces):
        self.current_member_forces = member_forces
        self.force_text_ids.clear()

        for (j1, j2), force in member_forces.items():
            member = tuple(sorted((j1, j2)))
            line_id = self.member_lines.get(member)
            if line_id:
                color = "red" if force < 0 else "green" if force > 0 else "yellow"
                self.canvas.itemconfig(line_id, fill=color)

                if self.show_forces and abs(force) > 1e-3:
                    x1, y1 = self.joints[j1]
                    x2, y2 = self.joints[j2]
                    mid_x = ((x1 + x2) / 2) * self.grid_spacing + self.offset_x
                    mid_y = self.offset_y - ((y1 + y2) / 2) * self.grid_spacing

                    force_text = f"{force:.2f}N"
                    text_width = len(force_text) * 7
                    text_height = 12

                    bg_x1 = mid_x - text_width / 2 - 2
                    bg_y1 = mid_y - text_height / 2 - 2
                    bg_x2 = mid_x + text_width / 2 + 2
                    bg_y2 = mid_y + text_height / 2 + 2
                    self.canvas.create_rectangle(bg_x1, bg_y1, bg_x2, bg_y2, fill="white", width=1)

                    text_id = self.canvas.create_text(mid_x, mid_y, text=force_text, font=("Arial", 12, "bold"), fill=color)
                    self.force_text_ids.append(text_id)

    def find_nearest_joint(self, x, y, threshold=10):
        for name, (jx, jy) in self.joints.items():
            cx = jx * self.grid_spacing + self.offset_x
            cy = self.offset_y - jy * self.grid_spacing
            if (x - cx) ** 2 + (y - cy) ** 2 < threshold ** 2:
                return name
        return None
