from __future__ import annotations

from typing import ClassVar, Iterable, Optional

from typing_extensions import TypeGuard

from textual.app import App, ComposeResult
from textual.widgets import Tree, ProgressBar, Input, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
from textual.widgets.option_list import Option, Separator
from textual.widgets.selection_list import Selection
from textual.screen import Screen 
from textual.await_complete import AwaitComplete
from textual.await_remove import AwaitRemove
from textual.binding import Binding, BindingType
from textual import events
from textual import work
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual import on
from textual.events import Mount
from textual.message import Message
from textual.reactive import reactive
from textual.await_complete import AwaitComplete 
from textual.widgets._directory_tree import DirEntry
from textual.widgets._tree import TreeNode
from textual.errors import TextualError
from textual.widgets._list_item import ListItem
from textual.widget import AwaitMount, Widget









#IMPORT MAIN CLASSES OF CUSTOMIZED WIDGETS FROM TEXTUAL
class HighlightableDirectoryTree(DirectoryTree):
    """DirectoryTree with path highlighting support."""

    class PathNotFoundError(TextualError):
        def __init__(self, path: Path) -> None:
            self.path = path

    def highlight_path(self, path: Path) -> AwaitComplete:
        """Highlight a path in the tree.

        Highlights a path that may be nested several levels deep in the tree.
        This can be done at all times, even when the tree has never been
        expanded and thus the directory contents containing the path have not
        been cached yet. This method will walk the tree, expanding nodes when
        necessary and waiting on the contents before taking another step until
        it arrives at the requested path. The node containing the path is
        subsequently highlighted.

        Args:
            path (Path): the path to highlight.

        Returns:
            AwaitComplete: An optionally awaitable that ensures the path is
                highlighted.
        """
        return AwaitComplete(self._highlight_path(path))

    async def _highlight_path(self, path: Path) -> None:
        """Highlight a path in the tree, while expanding parents.

        Args:
            path (Path): the path to highlight.
        """
        node = await self._expand_parents_and_find_node(path)
        self.move_cursor(node)

    async def _expand_parents_and_find_node(self, path: Path) -> TreeNode[DirEntry]:
        """Traverse all parts of the path and expand all parents.

        This method will traverse all parts of the path and expand all parents
        in the tree when necessary. Finally, the node containing the requested
        path is returned.

        Args:
            path (Path): the requested path that must become visible.

        Returns:
            TreeNode[DirEntry]: the tree node containing the requested path.
        """
        node = self.root
        for part in Path(path).parts:
            node = self._find_node_from_path(node, part)
            if not node.children:
                await self.reload_node(node)
            node.expand()
        return node

    def _find_node_from_path(
        self, parent: TreeNode[DirEntry], path: str
    ) -> TreeNode[DirEntry]:
        """Search a node's children for a specific path.

        The path must be a direct child of the parent. For example, if the
        parent's path is /home/alice, then the path may be /home/alice/work, or
        /home/alice/documents, but _not_ /home/alice/work/software since that is
        not a direct child of /home/alice.

        Args:
            parent (TreeNode[DirEntry]): the parent node.
            path (str): the path to search for.

        Raises:
            PathNotFoundError: raised when the path is not found.

        Returns:
            TreeNode[DirEntry]: the node containing the requested path.
        """
        root = parent.data.path.absolute()
        for node in parent.children:
            if str(node.data.path.relative_to(root)) == path:
                return node
        raise self.PathNotFoundError(path)


class MultiListItem(ListItem):
    """A widget that is an item within a `ListView`.

    A `ListItem` is designed for use within a
    [ListView][textual.widgets._list_view.ListView], please see `ListView`'s
    documentation for more details on use.
    """ 

    #highlighted = reactive(False)
    highlight_list = []
    """Is this item highlighted?"""

    def watch_highlighted(self, value: bool) -> None:
        #self.notify(str(self in self.highlight_list))



        if self in self.highlight_list:
            self.set_class(True, "-highlight")
        else:
            self.set_class(value, "-highlight")
        
        """
        conditions to highlight an object
        1 - current object selected
        2 - object in the list
        """

    def highlight_item(self, item) -> None:

        if item not in self.highlight_list:
            self.highlight_list.append(item)
            self.highlighted=True
        else:
            self.highlight_list.remove(item)
            self.highlighted = False

        for element in self.highlight_list:
            element.highlighted = True

    @on(events.Enter)
    @on(events.Leave)
    def on_enter_or_leave(self, event: events.Enter | events.Leave) -> None:
        event.stop()
        self.set_class(self.is_mouse_over, "-hovered")



class MultiListView(ListView):
    index_list = reactive[list]([], init=False)

    @property
    def highlighted_child(self) -> ListItem | None:
        """The currently highlighted ListItem, or None if nothing is highlighted."""
        if self.index is not None and 0 <= self.index < len(self._nodes):
            list_item = self._nodes[self.index]

            if self.index not in self.index_list:
                self.index_list.append(self.index)
            else:
                self.index_list.remove(self.index)

            #self.notify(str(self.index_list))


            assert isinstance(list_item, ListItem)
            return list_item
        else:
            return None



