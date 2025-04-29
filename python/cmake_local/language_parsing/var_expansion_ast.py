import development.exceptions
from . import var_expansion_tokens

#Because internal structure can shift, I choose to expose as little as possible.

class CMakeVarExpansionAST:
    class IteratorMetadataStruct:
        def __init__(
            self,
            node: 'CMakeVarExpansionAST.CMakeVarExpansionASTNode',
            child_index = 0
        ):
            self.node = node
            self.child_index = child_index
            self.skip = False

        def __str__(self):
            token_str = self.node.token[0] if self.node.token is not None else "ROOT"
            return f"IteratorMetadataStruct(node={token_str}, child_index={self.child_index}, skip={self.skip})"

    class TreeIterator:
        def __init__(self, start_node: 'CMakeVarExpansionAST.CMakeVarExpansionASTNode'):
            self.current_node = CMakeVarExpansionAST.IteratorMetadataStruct(start_node)
            self.metadata_stack = []


        def queue_nodes(self, node: 'CMakeVarExpansionAST.CMakeVarExpansionASTNode'):
            if node.has_children():
                for child in node.children:
                    self.metadata_stack.append(CMakeVarExpansionAST.IteratorMetadataStruct(child))

            
        #Handling children in ascending order of index implements
        #left-to-right ordering due to how the AST is constructed.
        def __next__(self):
            retval = None
            if self.current_node.node.has_children():
                if self.current_node.child_index < self.current_node.node.get_child_count():
                    if self.current_node.child_index == 0:
                        self.metadata_stack.append(self.current_node)
                    else:
                        self.current_node.child_index += 1

                    self.current_node = CMakeVarExpansionAST.IteratorMetadataStruct(
                        self.current_node.node.children[self.current_node.child_index]
                    )
                    retval = self.current_node.node
                else:
                    self.current_node = self.metadata_stack.pop()
            else:
                if len(self.metadata_stack) > 0:
                    self.current_node = self.metadata_stack.pop()
                    retval = self.current_node.node
                else:
                    raise StopIteration
            if self.current_node.node.is_root:
                return self.__next__()  #Cheat to get the next node
            return retval
        
    
    class BottomRightToUpperLeftTreeIterator:
        def __init__(self, start_node: 'CMakeVarExpansionAST._CMakeVarExpansionASTNode'):
            self.start_id = start_node.node_id
            self.current_node = None
            self.metadata_stack = [
                CMakeVarExpansionAST.IteratorMetadataStruct(start_node, start_node.get_child_count() - 1)
            ]
    
        def __next__(self):
            if not self.metadata_stack:
                raise StopIteration
            self.current_node = self.metadata_stack.pop()

            node = self.current_node.node
            if node.node_id == self.start_id:
                if node.has_children():
                    if self.current_node.child_index < 0:
                        raise StopIteration
                else:
                    if node.is_root:
                        raise StopIteration
                    return node.token

            if node.has_children() and self.current_node.child_index >= 0:
                node = node.children[self.current_node.child_index]
                while node.has_children():
                    self.metadata_stack.append(
                        CMakeVarExpansionAST.IteratorMetadataStruct(
                            node,
                            node.get_child_count() - 1
                        )
                    )
                    node = node.children[node.get_child_count() - 1]

                #self.current_node = self.metadata_stack[-1]
                #self.current_node = self.metadata_stack.pop()
            #else:
            #   self.current_node = self.metadata_stack.pop()
            #self.current_node = self.metadata_stack.pop()

            if self.metadata_stack:
                self.metadata_stack[-1].child_index -= 1
            return node.token
        
        def __iter__(self):
            return self

    #
    # Abstract base class for all AST nodes.
    #

    class _CMakeVarExpansionASTNode:
        def __init__(self, token, id: int):
            self.token = token
            self.parent = None
            self.depth = 0
            self.children = []
            self.is_root = False
            self.node_id = id

        def has_children(self):
            return len(self.children) > 0
        
        def get_child_count(self):
            return len(self.children)
        
    class RootASTNode(_CMakeVarExpansionASTNode):
        def __init__(self):
            super().__init__(None, -1)
            self.is_root = True

    class CMakeVarExpansionASTNode(_CMakeVarExpansionASTNode):
        def __init__(self, token: list, id: int):
            var_expansion_tokens.validate_token(token)
            super().__init__(token, id)

    def __init__(self):
        self.root = CMakeVarExpansionAST.RootASTNode()
        self.size = 0
        self.current_node = self.root
        self.ref_stack = []
        self.node_id_counter = -1

    def __iter__(self):
        if self.root is None:
            raise StopIteration
        return CMakeVarExpansionAST.TreeIterator(self.root)
    
    def __len__(self):
        return self.size

    def get_bottom_right_to_upper_left_iterator(self):
        if self.root is None:
            raise StopIteration
        return CMakeVarExpansionAST.BottomRightToUpperLeftTreeIterator(self.root)

    #
    # Backtracking methods:
    #
    def get_depth_of_node_by_token_ref(self, token):
        node = self.get_node_by_token_ref(token)
        return node.depth
    
    def get_node_by_depth_backtrack(self, backtrack_depth):
        node = None
        if self.current_node is None:
            raise development.exceptions.DevelopmentError("Cannot back trace when current node is None")
        if backtrack_depth < 0:
            raise development.exceptions.DevelopmentError("Backtrack depth cannot be negative")
        node = self.current_node
        for i in range(backtrack_depth):
            if node.parent is not None:
                node = node.parent
            else:
                raise development.exceptions.DevelopmentError(
                    "Cannot back trace when depth is greater than the number of nodes in the tree"
                )
        return node
    
    def get_node_by_token_ref(self, id):
        if len(self.ref_stack) == 0:
            raise development.exceptions.DevelopmentError("Cannot back trace when reference stack is empty")
        for node in self.ref_stack:
            if node.node_id == id:
                return node
        raise development.exceptions.DevelopmentError("Cannot back trace when token reference is not found")
    
    def backtrack_by_depth(self, depth):
        node = None
        if self.current_node is None:
            raise development.exceptions.DevelopmentError("Cannot back trace when current node is None")
        if depth < 0:
            raise development.exceptions.DevelopmentError("Depth cannot be negative")
        if self.root is None:
            raise development.exceptions.DevelopmentError("Cannot back trace when root is None")
        node = self.root
        for i in range(depth):
            if node.parent is not None:
                node = node.parent
            else:
                raise development.exceptions.DevelopmentError(
                    "Cannot back trace when depth is greater than the number of nodes in the tree"
                )
        self.current_node = node
        return node

    #
    # Add child methods:
    #
    def add_child_to_current_node(self, token):
        """Adds a child node to the current node.
        
        Args:
            token: The token to create the new node from
            
        Returns:
            The index of the newly added child in its parent's children array
        """
        child_index = None
        id = None
        node = None
        if self.root is None:
            raise development.exceptions.DevelopmentError("Root is None. This should never happen.")
        
        if self.current_node is None:
            raise development.exceptions.DevelopmentError("Current node is None. This should never happen.")

        self.node_id_counter += 1
        node_id = self.node_id_counter
        node = CMakeVarExpansionAST.CMakeVarExpansionASTNode(token, node_id)
        self.current_node.children.append(node)
        node.parent = self.current_node
        node.depth = self.current_node.depth + 1
        self.size += 1
        child_index = len(self.current_node.children) - 1
        self.ref_stack.append(node)
        return child_index, node_id

    def add_child_to_node_with_token_ref(self, token_id: int, new_node_token):
        """Adds a child node to the node with the specified token reference.
        
        Args:
            token: The token to create the new node from

        Returns:
            The index of the newly added child in its parent's children array
            
        Raises:
            DevelopmentError if node with token reference is not found
        """
        child_index = None
        token_id = None
        node = None
        if self.root is None:
            raise development.exceptions.DevelopmentError(
                "Cannot insert at node with token reference when root is None"
            )
        
        node = self.get_node_by_token_ref(token_id)
        
        #Add the child to the node:
        self.node_id_counter += 1
        node_id = self.node_id_counter
        child = CMakeVarExpansionAST.CMakeVarExpansionASTNode(new_node_token, node_id)
        node.children.append(child)
        child.parent = node
        child.depth = node.depth + 1
        self.size += 1
        child_index = len(node.children) - 1
        self.ref_stack.append(child)
        return child_index, node_id
    
    def add_sibling_by_token_ref(self, token_id: int, new_node_token):
        node = None
        new_node = None
        parent_node = None
        child_index = None
        node_id = None
        if self.current_node is None:
            raise development.exceptions.DevelopmentError(
                "Cannot add sibling when current node is None"
            )
        if self.current_node.parent is None:
            raise development.exceptions.DevelopmentError(
                "Cannot add sibling when parent is None"
            )
        node = self.get_node_by_token_ref(token_id)
        parent_node = node.parent
        self.node_id_counter += 1
        node_id = self.node_id_counter
        new_node = CMakeVarExpansionAST.CMakeVarExpansionASTNode(new_node_token, node_id)
        parent_node.children.append(new_node)
        new_node.parent = parent_node
        new_node.depth = parent_node.depth + 1
        self.size += 1
        child_index = len(parent_node.children) - 1
        self.ref_stack.append(new_node)
        return child_index, node_id

    #
    # Shift methods:
    #
    def shift_to_child_by_index(self, child_index: int):
        if self.current_node is None:
            raise development.exceptions.DevelopmentError(
                "Cannot shift to child when current node is None"
            )
        if child_index < 0:
            raise development.exceptions.DevelopmentError("Child index cannot be negative")
        if child_index >= len(self.current_node.children):
            raise development.exceptions.DevelopmentError("Child index is out of bounds")

        self.current_node = self.current_node.children[child_index]

    def shift_to_child_by_index_at_token_ref(self, token, child_index: int):
        if child_index < 0:
            raise development.exceptions.DevelopmentError("Child index cannot be negative") 
        elif child_index >= len(self.current_node.children):
            raise development.exceptions.DevelopmentError("Child index is out of bounds")

        if self.root is None:
            raise development.exceptions.DevelopmentError(
                "Cannot shift to child when root is None"
            )
        node = self.get_node_by_token_ref(token)

        self.current_node = node.children[child_index]

    #
    # Query methods:
    #
    def list_children_of_current_node(self):
        """Returns a copy of the list of children of the current node."""
        return self.current_node.children[:]

    #I prefer to reveal as little about the internal structure of the AST as possible.
    def shift_to_node_by_token_ref(self, token):
        self.current_node = self.get_node_by_token_ref(token)

    def merge_adjacent_tokens(self, merge_func, new_token):
        """Merges adjacent tokens of the given type using the provided merge function.
        
        Args:
            token_type: The type of token to merge
            merge_func: A function that takes two tokens and returns a merged token
            new_token: The token to merge with the current node's token
        """
        if self.current_node is None:
            raise development.exceptions.DevelopmentError("Current node is None. This should never happen.")
        
        if self.current_node.is_root:
            return False #Cannot merge adjacent tokens when current node is root
        
        if self.current_node.token is None:
            raise development.exceptions.DevelopmentError(
                "Current node's token is None. This should never happen except at the root node."
            )
        
        if self.current_node.token[0] == new_token[0]:
            # Merge the tokens using the provided function
            self.current_node.token = merge_func(
                self.current_node.token,
                new_token
            )
            return True
        return False

    def pretty_stringify(self, node=None, is_last=True):
        retval_arr = []
        longest_line_length = 0
        if node is None:
            if self.root is None:
                retval_arr.append("(empty tree)")
                return
            node = self.root
            is_last = True if (node.children is None or len(node.children) == 0) else False
        elif node == self.root:
            is_last = True if (node.children is None or len(node.children) == 0) else False

        # Stack elements are tuples of (node, prefix, is_last)
        stack = [(node, "", is_last)]

        while stack:
            current_node, current_prefix, current_is_last = stack.pop()
            
            # Print the current node
            if not current_node.children:
                branch = "└── " if current_is_last else "├── "
                if current_node.is_root:
                    retval_arr.append(f"{current_prefix}{branch}ROOT")
                    longest_line_length = max(longest_line_length, len(retval_arr[-1]))
                else:
                    retval_arr.append(f"{current_prefix}{branch}{current_node.token[0]}: {current_node.token[1]}")
                    longest_line_length = max(longest_line_length, len(retval_arr[-1]))
            else:
                if current_node.is_root:
                    retval_arr.append(f"{current_prefix}ROOT")
                    longest_line_length = max(longest_line_length, len(retval_arr[-1]))
                else:
                    retval_arr.append(f"{current_prefix}{current_node.token[0]}: {current_node.token[1]}")
                    longest_line_length = max(longest_line_length, len(retval_arr[-1]))

            # Update prefix for children
            new_prefix = current_prefix + ("    " if current_is_last else "│   ")

            # Push children onto stack in reverse order to maintain left-to-right printing
            for i in range(len(current_node.children) - 1, -1, -1):
                child = current_node.children[i]
                is_last_child = (i == len(current_node.children) - 1)
                stack.append((child, new_prefix, is_last_child))

        return "\n".join(retval_arr), longest_line_length
    
    def pretty_print(self):
        retval_arr, longest_line_length = self.pretty_stringify()
        print(retval_arr)
        print("-" * longest_line_length)

    