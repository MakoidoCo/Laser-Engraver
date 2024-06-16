import tkinter as tk
import logging, os, sys
from pprint import pprint
from typing import Union, Dict, List, Optional

sys.path.append(os.path.join(os.path.dirname(__file__),"../"))
from Config.setup import *

tkwidget_tree_log = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
tkwidget_tree_log.addHandler(HANDLER)
tkwidget_tree_log.setLevel(LOGLEVEL)

class TKWidgetTree:

    def __init__(self, root: tk.Tk, clock: int) -> None:
        """
        Initializes a WidgetTree object.

        Args:
            root (tk.Tk): The root of the widget tree.
            clock (int): Interval in milliseconds to update and repeat the widget tree print.
        """
        self.root = root
        self.clock = clock
        self.indent = 1
        self.first_call = True
        tkwidget_tree_log.info(f"WidgetTree initialized with root: {root}")


    def _is_widget_visible(self, widget: tk.Widget) -> bool:
        """
        Checks if a widget is visible on the screen.

        Args:
            widget (tk.Widget): The widget to check.

        Returns:
            bool: True if the widget is visible, False otherwise.
        """
        tkwidget_tree_log.debug(f"Checking visibility for widget: {widget}")
        root_x, root_y = self.root.winfo_rootx(), self.root.winfo_rooty()
        root_width, root_height = self.root.winfo_width(), self.root.winfo_height()
        widget_x, widget_y = widget.winfo_rootx() - root_x, widget.winfo_rooty() - root_y
        widget_width, widget_height = widget.winfo_width(), widget.winfo_height()

        is_visible = widget_x >= 0 and widget_y >= 0 and widget_x + widget_width <= root_width and widget_y + widget_height <= root_height
        tkwidget_tree_log.debug(f"Widget {widget} visibility: {is_visible}")
        return is_visible


    def _is_widget_tapped(self, widget: tk.Widget) -> bool:
        """
        Checks if a widget is tapped (covered) by another widget.

        Args:
            widget (tk.Widget): The widget to check.

        Returns:
            bool: True if the widget is tapped, False otherwise.
        """
        containing_widget = self.root.winfo_containing(widget.winfo_rootx(), widget.winfo_rooty())
        return containing_widget != widget


    def _widget_tree_dict(self, widget: tk.Widget, depth: int = 0, include_children: bool = True) -> Dict:
        """
        Creates a dictionary representing the widget tree from a given widget.

        Args:
            widget (tk.Widget): The widget from which to create the dictionary.
            depth (int): The current depth in the widget tree.
            include_children (bool): Indicates whether to include the widget's children in the dictionary.
            include_widget (bool): Indicates whether to include the widget itself in the dictionary.

        Returns:
            dict: The dictionary representing the widget tree.
        """
        tkwidget_tree_log.debug(f"Creating dictionary for widget: {widget} at depth: {depth}")
        widget_info = {
            "class": widget.winfo_class(),
            "name": widget.winfo_name(),
            "depth": depth + 1,
            "tapped": self._is_widget_tapped(widget),
            "mapped": bool(widget.winfo_ismapped()),
            "viewable": bool(widget.winfo_viewable()),
            "on_screen": self._is_widget_visible(widget),
            "manager": widget.winfo_manager() or False,
            "widget": widget,
            "children": []
        }

        if include_children:
            children = widget.winfo_children()
            for child in children:
                widget_info["children"].append(self._widget_tree_dict(child, depth + 1))

        tkwidget_tree_log.debug(f"Widget dictionary created: {widget_info}")
        return widget_info


    def get_parent(self, widget: tk.Widget) -> Union[str, None]:
        """
        Get the parent widget of a given widget.

        Args:
            widget (tk.Widget): The widget whose parent to find.

        Returns:
            tk.Widget or None: The parent widget if found, otherwise None.
        """
        parent_id = widget.winfo_parent()
        if parent_id:
            parent_widget = self.root.nametowidget(parent_id)
            tkwidget_tree_log.debug(f"Parent widget of {widget}: {parent_widget}")
            return parent_widget
        else:
            tkwidget_tree_log.debug(f"{widget} has no parent widget")
            return None


    def get_parents(self, widget: tk.Widget, include_self: bool = True, max_parent: int = None) -> List[tk.Widget]:
        """
        Get the list of all parents of a given widget, including itself.

        Args:
            widget (tk.Widget): The widget whose parents to find.
            include_self (bool): Whether to include the widget itself in the list.
            max_parent (int): Maximum number of parents to include. If None, includes all parents.

        Returns:
            list of tk.Widget: The list of parent widgets.
        """
        if max_parent is None:
            max_parent = float('inf')

        parents = []
        current_widget = widget if include_self else self.get_parent(widget)
        while current_widget and max_parent > 0:
            parents.append(current_widget)
            current_widget = self.get_parent(current_widget)
            max_parent -= 1
        tkwidget_tree_log.debug(f"Parents of {widget}: {parents}")
        return parents


    def get_child(self, parent: tk.Widget, child_name: str) -> Union[tk.Widget, None]:
        """
        Get the child widget of a given parent widget by its name.

        Args:
            parent (tk.Widget): The parent widget.
            child_name (str): The name of the child widget to find.

        Returns:
            tk.Widget or None: The child widget if found, otherwise None.
        """
        for child in parent.winfo_children():
            if child.winfo_name() == child_name:
                tkwidget_tree_log.debug(f"Child widget '{child_name}' found under parent '{parent.winfo_name()}': {child}")
                return child
        tkwidget_tree_log.debug(f"Child widget '{child_name}' not found under parent '{parent.winfo_name()}'")
        return None


    def get_children(self, parent: tk.Widget, recursive: bool = False, max_children: int = None) -> List[tk.Widget]:
        """
        Get the list of children widgets of a given parent widget.

        Args:
            parent (tk.Widget): The parent widget.
            recursive (bool): Whether to include children of children recursively.
            max_children (int): Maximum number of children to include. If None, includes all children.

        Returns:
            list of tk.Widget: The list of children widgets.
        """
        children = parent.winfo_children()
        if max_children is not None and max_children >= 0:
            children = children[:max_children]

        if recursive and max_children is not None and max_children > 0:
            for child in parent.winfo_children():
                children.extend(self.get_children(child, recursive=True, max_children=max_children-len(children)))

        tkwidget_tree_log.debug(f"Children of {parent.winfo_name()}: {children}")
        return children


    def get_descendants(self, widget, max_depth=None):
        descendants = []
        def traverse_descendants(parent, depth):
            nonlocal descendants
            if max_depth is not None and depth >= max_depth:
                return
            children = parent.winfo_children()
            descendants.extend(children)
            for child in children:
                traverse_descendants(child, depth + 1)
        traverse_descendants(widget, 0)
        return descendants


    def get_widget_exist(self, widget: tk.Widget) -> bool:
        """
        Checks if a widget exists in the GUI.

        Args:
            widget (tk.Widget): The widget to check.

        Returns:
            bool: True if the widget exists, False otherwise.
        """
        exists = widget.winfo_exists()
        tkwidget_tree_log.debug(f"Widget {widget} exists: {exists}")
        return bool(exists)


    def get_widget_tree(self) -> Dict:
        """
        Gets the widget tree structure starting from the root.

        Returns:
            dict: The dictionary representing the widget tree structure.
        """
        tkwidget_tree_log.debug(f"Getting widget tree for root: {self.root}")
        widget_tree = self._widget_tree_dict(self.root)
        tkwidget_tree_log.debug(f"Widget tree: {widget_tree}")
        return widget_tree


    def print_widget_tree(self) -> None:
        """
        Prints the widget tree structure as a formatted JSON string.
        """
        tkwidget_tree_log.debug("Printing widget tree")
        widget_tree = self.get_widget_tree()

        if self.first_call:
            self.first_call = False
            tkwidget_tree_log.debug("First call detected, scheduling a second print")
            self.root.after(500, self.print_widget_tree)
        else:
            tkwidget_tree_log.info("Widget Tree:")
            pprint(widget_tree, indent=self.indent, sort_dicts=False)
            print()


    def find_widget_by_name(self, name: str, include_children: bool = True, widget: Optional[tk.Widget] = None, current_depth: int = 0, max_depth: Optional[int] = None) -> Union[Dict, None]:
        """
        Finds a widget in the widget tree by its name.

        Args:
            name (str): The name of the widget to find.
            include_children (bool): Indicates whether to include the widget's children in the search.
            widget (tk.Widget): The starting widget for the search (defaults to the root if None).
            current_depth (int): The current depth in the widget tree.
            max_depth (int): The maximum depth to search within the widget tree.

        Returns:
            dict or None: The dictionary representing the found widget, or None if not found.
        """
        if widget is None:
            widget = self.root
        tkwidget_tree_log.debug(f"Finding widget by name: {name}, current widget: {widget}, depth: {current_depth}, max_depth: {max_depth}")

        if (max_depth is None or current_depth <= max_depth) and widget.winfo_name() == name:
            tkwidget_tree_log.debug(f"Widget {widget} found by name: {name}")
            return self._widget_tree_dict(widget, current_depth, include_children)

        if max_depth is not None and current_depth >= max_depth:
            tkwidget_tree_log.debug(f"Reached max depth: {max_depth} for widget: {widget}")
            return None

        for child in widget.winfo_children():
            result = self.find_widget_by_name(name, include_children, child, current_depth + 1, max_depth)
            if result:
                return result
        return None


    def find_widget(self, target_widget: tk.Widget, widget: Optional[tk.Widget] = None, current_depth: int = 0, max_depth: Optional[int] = None) -> Union[Dict, None]:
        """
        Finds a widget in the widget tree by its reference.

        Args:
            target_widget (tk.Widget): The target widget to find.
            widget (tk.Widget): The starting widget for the search (defaults to the root if None).
            current_depth (int): The current depth in the widget tree.
            max_depth (int): The maximum depth to search within the widget tree.
            include_widget (bool): Indicates whether to include the found widget in the result.

        Returns:
            dict or None: The dictionary representing the found widget, or None if not found.
        """
        if widget is None:
            widget = self.root
        tkwidget_tree_log.debug(f"Finding widget by reference: {target_widget}, current widget: {widget}, depth: {current_depth}, max_depth: {max_depth}")

        if (max_depth is None or current_depth <= max_depth) and widget == target_widget:
            tkwidget_tree_log.debug(f"Target widget {target_widget} found")
            return self._widget_tree_dict(widget, current_depth)

        if max_depth is not None and current_depth >= max_depth:
            tkwidget_tree_log.debug(f"Reached max depth: {max_depth} for widget: {widget}")
            return None

        for child in widget.winfo_children():
            result = self.find_widget(target_widget, child, current_depth + 1, max_depth)
            if result:
                return result
        return None


    def update_and_repeat(self) -> None:
        """
        Updates and repeats the widget tree print at specified intervals.
        """
        tkwidget_tree_log.debug("Updating and repeating widget tree print")
        self.print_widget_tree()
        self.root.after(self.clock, self.update_and_repeat)



class ExampleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Widget Tree")
        self.viewer = TKWidgetTree(self, clock=5000)

        frame1 = tk.Frame(self, width=300, height=200, bg="lightblue", name="frame1")
        button1 = tk.Button(frame1, width=10, height=1, text="Button 1", name="button1")
        button1.pack(pady=10, padx=10)
        frame1.pack(pady=20, padx=20)

        frame2 = tk.Frame(self, width=300, height=200, bg="lightblue", name="frame2")
        button2 = tk.Button(frame2, width=10, height=1, text="Button 2", name="button2")
        button2.pack(pady=10, padx=10)
        frame2.pack(pady=20, padx=20)

        frame3 = tk.Frame(frame2, width=200, height=100, bg="lightgreen", name="frame3")
        label3 = tk.Label(frame3, text="Label 3", bg="lightgreen", name="label3")
        label3.pack(pady=5, padx=5)
        frame3.pack(pady=10, padx=10)

        frame4 = tk.Frame(frame3, width=150, height=80, bg="lightyellow", name="frame4")
        label4 = tk.Label(frame4, text="Label 4", bg="lightyellow", name="label4")
        label4.pack(pady=5, padx=5)
        frame4.pack(pady=5, padx=5)

        frame5 = tk.Frame(frame4, width=100, height=50, bg="lightcoral", name="frame5")
        label5 = tk.Label(frame5, text="Label 5", bg="lightcoral", name="label5")
        label5.pack(pady=5, padx=5)
        frame5.pack(pady=5, padx=5)

        entry = tk.Entry(self, width=20, name="entry")
        entry.pack(pady=10)

        check_button = tk.Checkbutton(self, text="Check Button", name="check_button")
        check_button.pack(pady=10)

        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Save")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        tkwidget_tree_log.info(f"Widget 'button1' exists: {self.viewer.get_widget_exist(button1)}")
        button1.destroy()
        tkwidget_tree_log.info(f"Widget 'button1' exists after destruction: {self.viewer.get_widget_exist(button1)}")

        parent_widget = self.viewer.get_parent(button2)
        tkwidget_tree_log.info(f"Parent widget of button2: {parent_widget}")

        parents_all = self.viewer.get_parents(button2)
        tkwidget_tree_log.info(f"All parents of button2: {parents_all}")

        frame2 = self.nametowidget(".frame2")
        button2_child = self.viewer.get_child(frame2, "button2")
        tkwidget_tree_log.info(f"Child widget 'button2' under frame2: {button2_child}")

        all_children = self.viewer.get_children(frame2)
        tkwidget_tree_log.info(f"All children under frame2: {all_children}")

        found_widget = self.viewer.find_widget_by_name("button2")
        tkwidget_tree_log.info(f"Widget found by name (no depth): {pprint(found_widget, indent=2)}")

        found_widget = self.viewer.find_widget_by_name("button2", max_depth=1)
        tkwidget_tree_log.info(f"Widget found by name (with depth=1): {found_widget}")

        found_widget = self.viewer.find_widget(button2)
        tkwidget_tree_log.info(f"Widget found by reference (no depth): {pprint(found_widget, indent=2)}")

        found_widget = self.viewer.find_widget(button2, max_depth=1)
        tkwidget_tree_log.info(f"Widget found by reference (with depth=1): {found_widget}")

        parent_widget = self.viewer.get_parent(button2)
        tkwidget_tree_log.info(f"Parent widget of button2: {parent_widget}")

        parents_all = self.viewer.get_parents(button2)
        tkwidget_tree_log.info(f"All parents of button2 (no limit): {parents_all}")

        parents_limited = self.viewer.get_parents(button2, max_parent=7)
        tkwidget_tree_log.info(f"Parents of button2 limited to 1 level: {parents_limited}")

        frame2 = self.nametowidget(".frame2")
        button2_child = self.viewer.get_child(frame2, "button2")
        tkwidget_tree_log.info(f"Child widget 'button2' under frame2: {button2_child}")

        children_all = self.viewer.get_children(frame2)
        tkwidget_tree_log.info(f"All children under frame2 (no limit): {children_all}")

        children_limited = self.viewer.get_children(frame2, max_children=9)
        tkwidget_tree_log.info(f"Children of frame2 limited to 1 level: {children_limited}")

        descendants = self.viewer.get_descendants(frame2, max_depth=2)
        tkwidget_tree_log.info(f"Descendants of frame2 up to depth 2: {[descendants]}")


        self.viewer.update_and_repeat()

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = ExampleApp()
    app.run()