
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QSizePolicy, QPushButton, QVBoxLayout, QWidget
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from Components.CollapsibleOverlay import CollapsibleOverlay

class GraphDisplay(CollapsibleOverlay):

    def __init__(self, parent=None):

        self.full_width = 300  # Total width when expanded
        self.collapsed_width = 20

        self.above_height_amount = 0
        #used to lift the bottom ogf the overlay from the bottom of the application
        self.control_panel_height_reduction = 110 #TODO: find a better way to provide and access this information
        
        self.expanded = True
        self.tle_display = parent.tle_display

        super().__init__(parent)
        self.setStyleSheet("background-color: #f0f0f0; border: 1px solid gray;")
        self.setParent(parent)
        self.setVisible(True)

        self.set_up_content_window()
        
        self.set_up_collapse_button()
        
        self.update_height()
        self.toggle_width()

    def set_up_content_window(self):
        self.overlay = QWidget(self)
        print(self.parent().width())
        self.overlay.setGeometry(30, 0, self.full_width if self.expanded else self.collapsed_width, self.parent().height() - self.overlay.height() - self.control_panel_height_reduction)
        self.overlay.setStyleSheet("background-color: #dddddd;")
        self.overlay.setVisible(True)

        self.content_window = QVBoxLayout()
        self.content_window.setObjectName("Content Window")

        self.overlay.setLayout(self.content_window)

    def set_up_adjacency_graph(self):
        # Layout for graphs and controls
        self.graphLayout = QVBoxLayout()
        self.content_window.addLayout(self.graphLayout, stretch=5)

        # Matplotlib figure and canvas for adjacency matrix and network graph
        self.figure, self.axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graphLayout.addWidget(self.canvas, stretch=10)
    
    def set_up_connection_graph(self):
            pass
    
    def set_up_collapse_button(self):
        self.toggle_button = QPushButton("▼\nE\nx\np\na\nn\nd", self)
        self.toggle_button.setGeometry(self.parent().width() - 20, self.above_height_amount, 20, self.height())

        self.opacity_effect = QGraphicsOpacityEffect(self.toggle_button)
        self.toggle_button.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

        # Set up enter/leave events
        self.toggle_button.installEventFilter(self)

        self.toggle_button.clicked.connect(self.toggle_width)

    def toggle_width(self):
        self.expanded = not self.expanded

        #start_rect = self.geometry()
        end_width = self.full_width if self.expanded else self.collapsed_width
        #end_rect = QRect(0, 0, self.parent().width(), end_height)
        self.setGeometry(self.parent().width() - 20, 0, end_width, self.height())  # Start with just the button height

        self.overlay.setVisible(self.expanded)
        self.toggle_button.setText("▲\nC\no\nl\nl\na\np\ns\ne" if self.expanded else "▼\nE\nx\np\na\nn\nd")
        
    def update_height(self):
        target_width = self.full_width if self.expanded else self.collapsed_width
        target_height = self.parent().height() - self.above_height_amount - self.control_panel_height_reduction

        self.setGeometry(0, self.above_height_amount, target_width, target_height)  # Start with just the button height
        self.toggle_button.setGeometry(0, self.above_height_amount, 20, target_height)

#        
#
#        # Controls layout
#        self.controlsLayout = QVBoxLayout()
#        self.graphLayout.addLayout(self.controlsLayout, stretch=2)
#
#        def update_graphs(self, positions):
#        #Update the adjacency matrix and network graph plots.
#        try:
#            adj_matrix, keys = self.simulation.generate_adjacency_matrix(positions)
#            self.axes[0].cla()
#            self.axes[1].cla()
#
#            self.axes[0].imshow(adj_matrix, cmap='Blues', interpolation='none', aspect='equal')
#            self.axes[0].set_title('Adjacency Matrix')
#            self.axes[0].set_xticks(np.arange(len(keys)))
#            self.axes[0].set_yticks(np.arange(len(keys)))
#            self.axes[0].set_xticklabels(keys, rotation=90)
#            self.axes[0].set_yticklabels(keys)
#
#            G = nx.from_numpy_array(adj_matrix)
#            pos = nx.spring_layout(G)
#            nx.draw(G, pos, ax=self.axes[1], with_labels=True, node_color='skyblue')
#            self.axes[1].set_title('Network Graph')
#
#            self.canvas.draw()
#        except ValueError as e:
#            QMessageBox.critical(self, "Error", f"An error occurred during graph update: {e}")
#
#
#       def calculate_distance(self, pos1, pos2):
#               # Calculate the Euclidean distance between two satellite positions.
#               return np.linalg.norm(np.array(pos1) - np.array(pos2))
#       
#           def generate_adjacency_matrix(self, positions, distance_threshold=10000):
#               # Generate an adjacency matrix based on the distances between satellites.
#               keys = list(positions.keys())
#               size = len(keys)
#               adj_matrix = np.zeros((size, size), dtype=int)
#       
#               # Compute distances between all satellite pairs and populate the adjacency matrix
#               for i in range(size):
#                   for j in range(i + 1, size):
#                       dist = self.calculate_distance(positions[keys[i]], positions[keys[j]])
#                       adj_matrix[i, j] = adj_matrix[j, i] = 1 if dist < distance_threshold else 0
#       
#               return adj_matrix, keys
