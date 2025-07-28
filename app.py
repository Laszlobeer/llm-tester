import sys
import requests
import time
import json
import concurrent.futures
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QProgressBar, QTableWidget,
                             QTableWidgetItem, QHeaderView, QSplitter, QTextEdit, 
                             QMessageBox, QGroupBox, QSpinBox, QTabWidget, QStyleFactory)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

# Configuration
OLLAMA_HOST = "http://localhost:11434"
WARMUP_RUNS = 1  # Initial runs to warm up the model
CONCURRENCY_LEVEL = 10  # Fixed concurrency level

# Generate 100 diverse benchmark prompts
BENCHMARK_PROMPTS = [
    "Explain quantum computing in simple terms",
    "Write a Python function to calculate Fibonacci sequence",
    "write a short story",
    "write a poem",
    "Describe three benefits of renewable energy",
    "What is the capital of France? Just state the city name.",
    "How does photosynthesis work in plants?",
    "Create a short poem about the changing seasons",
    "Describe the process of cellular respiration",
    "What are the main differences between Python and JavaScript?",
    "Explain the concept of object-oriented programming",
    "How does a neural network learn from data?",
    "Describe the water cycle in nature",
    "What causes earthquakes and how are they measured?",
    "Explain the theory of relativity in simple terms",
    "How do vaccines work to protect against diseases?",
    "Describe the structure of DNA and its role in genetics",
    "What is blockchain technology and how does it work?",
    "Explain the difference between HTTP and HTTPS",
    "How do clouds form in the atmosphere?",
    "Describe the process of evolution by natural selection",
    "What are black holes and how are they formed?",
    "Explain how a CPU processes instructions",
    "Describe the lifecycle of a butterfly",
    "What is machine learning and give an example of its application",
    "Explain the greenhouse effect and its impact on climate",
    "How do batteries store and release electrical energy?",
    "Describe the human digestive system",
    "What are the main layers of the Earth's atmosphere?",
    "Explain how solar panels convert sunlight into electricity",
    "Describe the process of mitosis in cell division",
    "What is the difference between RAM and ROM?",
    "Explain how GPS technology determines location",
    "Describe the structure and function of the human heart",
    "What causes the tides in Earth's oceans?",
    "Explain the concept of supply and demand in economics",
    "How do airplanes generate lift to fly?",
    "Describe the process of protein synthesis in cells",
    "What is artificial intelligence and what are its main branches?",
    "Explain how the immune system fights infections",
    "Describe the water treatment process for making it drinkable",
    "What are the main components of a computer network?",
    "Explain the difference between kinetic and potential energy",
    "How do electric motors convert electricity into motion?",
    "Describe the process of fossil fuel formation",
    "What is the carbon cycle and why is it important?",
    "Explain how microwave ovens heat food",
    "Describe the structure of the solar system",
    "What causes the phases of the moon?",
    "Explain how antibiotics fight bacterial infections",
    "Describe the process of DNA replication",
    "What is cryptography and how is it used in cybersecurity?",
    "Explain how nuclear power plants generate electricity",
    "Describe the human respiratory system",
    "What are enzymes and what role do they play in metabolism?",
    "Explain the concept of natural selection with an example",
    "How do optical fibers transmit data?",
    "Describe the process of soil formation",
    "What are the main types of renewable energy sources?",
    "Explain how the Doppler effect changes sound frequency",
    "Describe the structure and function of the human brain",
    "What causes volcanic eruptions?",
    "Explain how digital cameras capture images",
    "Describe the nitrogen cycle in ecosystems",
    "What is the difference between weather and climate?",
    "Explain how hybrid cars save fuel",
    "Describe the process of osmosis in cells",
    "What are stem cells and why are they important?",
    "Explain how radar systems detect objects",
    "Describe the process of fermentation in food production",
    "What is the big bang theory in cosmology?",
    "Explain how touchscreens detect input",
    "Describe the human circulatory system",
    "What causes lightning and thunder during storms?",
    "Explain the concept of opportunity cost in economics",
    "How do wind turbines generate electricity?",
    "Describe the process of metamorphosis in frogs",
    "What is the difference between analog and digital signals?",
    "Explain how vaccines create immunity",
    "Describe the structure of an atom",
    "What are the main types of rocks and how do they form?",
    "Explain how refrigerators keep food cold",
    "Describe the process of pollination in plants",
    "What causes the aurora borealis (northern lights)?",
    "Explain how voice recognition software works",
    "Describe the human skeletal system",
    "What is the difference between mass and weight?",
    "How do submarines dive and surface?",
    "Describe the process of eutrophication in water bodies",
    "What is machine translation and how does it work?",
    "Explain how solar eclipses occur",
    "Describe the process of cellular differentiation",
    "What causes ocean currents?",
    "Explain how biometric authentication systems work",
    "Describe the structure and function of the liver",
    "What is dark matter in astronomy?",
    "How do speakers convert electrical signals into sound?",
    "Describe the process of erosion and deposition",
    "What is the difference between AC and DC electricity?",
    "Explain how 3D printing creates objects",
    "Describe the human nervous system",
    "What causes seasons on Earth?"
]

class BenchmarkWorker(QThread):
    progress_updated = pyqtSignal(int, str)
    benchmark_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, model_name, task_count):
        super().__init__()
        self.model_name = model_name
        self.task_count = task_count
        self.cancelled = False
    
    def run(self):
        try:
            # Warm-up runs
            for i in range(WARMUP_RUNS):
                if self.cancelled:
                    return
                self.progress_updated.emit(0, f"Warming up model ({i+1}/{WARMUP_RUNS})...")
                self._run_benchmark("Warm up run")
            
            # Select random prompts for the benchmark
            selected_prompts = random.sample(BENCHMARK_PROMPTS, self.task_count)
            
            # Prepare for benchmark
            self.progress_updated.emit(0, f"Preparing {self.task_count} tasks...")
            start_time = time.time()
            results = []
            completed = 0
            
            # Run benchmark with thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY_LEVEL) as executor:
                futures = {executor.submit(self._run_benchmark, prompt): prompt for prompt in selected_prompts}
                
                for future in concurrent.futures.as_completed(futures):
                    if self.cancelled:
                        return
                    
                    completed += 1
                    progress = int((completed / self.task_count) * 100)
                    status = f"Completed {completed}/{self.task_count} tasks"
                    self.progress_updated.emit(progress, status)
                    
                    try:
                        metrics = future.result()
                        if metrics:
                            results.append(metrics)
                    except Exception as e:
                        print(f"Task failed: {str(e)}")
            
            # Calculate overall metrics
            total_time = time.time() - start_time
            throughput = self.task_count / total_time
            latency_avg = sum(r['latency'] for r in results) / len(results) if results else 0
            tokens_sec_avg = sum(r['tokens_sec'] for r in results) / len(results) if results else 0
            
            # Emit results
            self.benchmark_completed.emit({
                "model": self.model_name,
                "task_count": self.task_count,
                "total_time": total_time,
                "throughput": throughput,
                "latency_avg": latency_avg,
                "tokens_sec_avg": tokens_sec_avg,
                "results": results
            })
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def _run_benchmark(self, prompt):
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0}  # For consistent results
        }
        
        start_time = time.perf_counter()
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        end_time = time.perf_counter()
        
        if response.status_code != 200:
            raise Exception(f"API Error: {response.text}")
        
        data = response.json()
        eval_duration = data.get('eval_duration', 0) / 1e9  # ns to seconds
        eval_count = data.get('eval_count', 0)
        tokens_sec = eval_count / eval_duration if eval_duration > 0 else 0
        
        return {
            "prompt": prompt,
            "latency": end_time - start_time,
            "eval_duration": eval_duration,
            "eval_count": eval_count,
            "tokens_sec": tokens_sec
        }
    
    def cancel(self):
        self.cancelled = True

class OllamaBenchmarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ollama Model Benchmark - Dark Theme")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Title
        title = QLabel("Ollama Model Benchmark")
        title_font = QFont("Arial", 18, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #61dafb; padding: 10px;")
        main_layout.addWidget(title)
        
        # Configuration group
        config_group = QGroupBox("Benchmark Configuration")
        config_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #61dafb;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                color: #61dafb;
            }
        """)
        config_layout = QHBoxLayout(config_group)
        config_layout.setSpacing(20)
        
        # Model selection
        model_layout = QVBoxLayout()
        model_label = QLabel("Select Model:")
        model_label.setFont(QFont("Arial", 10))
        model_label.setStyleSheet("color: #ddd;")
        
        self.model_combo = QComboBox()
        self.model_combo.setFont(QFont("Arial", 10))
        self.model_combo.setMinimumWidth(300)
        self.model_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #333;
                color: #eee;
            }
            QComboBox QAbstractItemView {
                background-color: #333;
                color: #eee;
                selection-background-color: #444;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        
        self.refresh_btn = QPushButton("Refresh Models")
        self.refresh_btn.setFont(QFont("Arial", 10))
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a5fb4;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1c71d8;
            }
            QPushButton:disabled {
                background-color: #555;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_models)
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(self.refresh_btn)
        
        # Task count settings
        tasks_layout = QVBoxLayout()
        tasks_label = QLabel("Number of Tasks:")
        tasks_label.setFont(QFont("Arial", 10))
        tasks_label.setStyleSheet("color: #ddd;")
        
        self.tasks_spin = QSpinBox()
        self.tasks_spin.setFont(QFont("Arial", 10))
        self.tasks_spin.setRange(1, 200)
        self.tasks_spin.setValue(100)
        self.tasks_spin.setStyleSheet("""
            QSpinBox {
                padding: 6px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #333;
                color: #eee;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
            }
        """)
        
        tasks_layout.addWidget(tasks_label)
        tasks_layout.addWidget(self.tasks_spin)
        
        # Add layouts to config group
        config_layout.addLayout(model_layout)
        config_layout.addLayout(tasks_layout)
        config_layout.addStretch()
        main_layout.addWidget(config_group)
        
        # Benchmark controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        self.start_btn = QPushButton("Start Benchmark")
        self.start_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #26a269;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ec27e;
            }
            QPushButton:disabled {
                background-color: #555;
            }
        """)
        self.start_btn.clicked.connect(self.start_benchmark)
        
        self.cancel_btn = QPushButton("Cancel Benchmark")
        self.cancel_btn.setFont(QFont("Arial", 10))
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #c01c28;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e01b24;
            }
            QPushButton:disabled {
                background-color: #555;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_benchmark)
        self.cancel_btn.setEnabled(False)
        
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.cancel_btn)
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFont(QFont("Arial", 9))
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 5px;
                text-align: center;
                background-color: #252525;
            }
            QProgressBar::chunk {
                background-color: #1a5fb4;
                border-radius: 4px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to start benchmark")
        self.status_label.setFont(QFont("Arial", 9))
        self.status_label.setStyleSheet("color: #999;")
        main_layout.addWidget(self.status_label)
        
        # Results area
        results_splitter = QSplitter(Qt.Vertical)
        
        # Summary panel
        summary_panel = QWidget()
        summary_layout = QVBoxLayout(summary_panel)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        
        summary_label = QLabel("Benchmark Summary")
        summary_label.setFont(QFont("Arial", 10, QFont.Bold))
        summary_label.setStyleSheet("color: #61dafb;")
        
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(4)
        self.summary_table.setHorizontalHeaderLabels(["Model", "Tasks", "Total Time", "Throughput (tasks/s)"])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.summary_table.setRowCount(0)
        self.summary_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.summary_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #444;
                background-color: #252525;
                color: #ddd;
            }
            QHeaderView::section {
                background-color: #1a5fb4;
                color: white;
                font-weight: bold;
                padding: 5px;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        
        summary_layout.addWidget(summary_label)
        summary_layout.addWidget(self.summary_table)
        
        # Results panel
        results_panel = QWidget()
        results_layout = QVBoxLayout(results_panel)
        results_layout.setContentsMargins(0, 0, 0, 0)
        
        results_label = QLabel("Task Details")
        results_label.setFont(QFont("Arial", 10, QFont.Bold))
        results_label.setStyleSheet("color: #61dafb;")
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Prompt", "Latency (s)", "Tokens/s", "Status"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #444;
                background-color: #252525;
                color: #ddd;
            }
            QHeaderView::section {
                background-color: #1a5fb4;
                color: white;
                font-weight: bold;
                padding: 5px;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        
        results_layout.addWidget(results_label)
        results_layout.addWidget(self.results_table)
        
        # Add panels to splitter
        results_splitter.addWidget(summary_panel)
        results_splitter.addWidget(results_panel)
        results_splitter.setSizes([200, 400])
        main_layout.addWidget(results_splitter, 1)
        
        # Initialize
        self.benchmark_worker = None
        self.benchmark_results = []
        self.load_models()
    
    def apply_dark_theme(self):
        # Set dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        # Set disabled colors
        dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        
        # Apply palette
        QApplication.setPalette(dark_palette)
        QApplication.setStyle("Fusion")
    
    def load_models(self):
        self.model_combo.clear()
        self.status_label.setText("Loading installed models...")
        
        try:
            response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
            response.raise_for_status()
            models = [model['name'] for model in response.json().get('models', [])]
            
            if models:
                self.model_combo.addItems(models)
                self.status_label.setText(f"Loaded {len(models)} models. Ready to benchmark.")
            else:
                self.status_label.setText("No models found. Please install models in Ollama.")
            
            self.start_btn.setEnabled(len(models) > 0)
        except Exception as e:
            self.status_label.setText(f"Error loading models: {str(e)}")
            self.start_btn.setEnabled(False)
    
    def start_benchmark(self):
        if self.model_combo.currentText() == "":
            QMessageBox.warning(self, "No Model Selected", "Please select a model to benchmark.")
            return
        
        # Reset UI
        self.results_table.setRowCount(0)
        
        # Disable controls during benchmark
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.model_combo.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.tasks_spin.setEnabled(False)
        
        # Create and start worker thread
        model_name = self.model_combo.currentText()
        task_count = self.tasks_spin.value()
        
        self.benchmark_worker = BenchmarkWorker(model_name, task_count)
        self.benchmark_worker.progress_updated.connect(self.update_progress)
        self.benchmark_worker.benchmark_completed.connect(self.benchmark_finished)
        self.benchmark_worker.error_occurred.connect(self.handle_error)
        self.benchmark_worker.start()
    
    def cancel_benchmark(self):
        if self.benchmark_worker and self.benchmark_worker.isRunning():
            self.benchmark_worker.cancel()
            self.benchmark_worker.terminate()
            self.status_label.setText("Benchmark cancelled")
            self.progress_bar.setValue(0)
            self.reset_ui()
    
    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def benchmark_finished(self, results):
        self.status_label.setText("Benchmark completed successfully")
        self.progress_bar.setValue(100)
        self.reset_ui()
        self.display_results(results)
    
    def handle_error(self, error_message):
        self.status_label.setText(f"Error: {error_message}")
        self.progress_bar.setValue(0)
        self.reset_ui()
        QMessageBox.critical(self, "Benchmark Error", f"An error occurred:\n\n{error_message}")
    
    def reset_ui(self):
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.model_combo.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.tasks_spin.setEnabled(True)
    
    def display_results(self, results):
        # Store results
        self.benchmark_results.append(results)
        
        # Update summary table
        self.summary_table.setRowCount(len(self.benchmark_results))
        
        for i, result in enumerate(self.benchmark_results):
            model_item = QTableWidgetItem(result["model"])
            tasks_item = QTableWidgetItem(str(result["task_count"]))
            time_item = QTableWidgetItem(f"{result['total_time']:.2f}")
            throughput_item = QTableWidgetItem(f"{result['throughput']:.2f}")
            
            # Color code throughput for performance
            throughput = result['throughput']
            if throughput > 5:
                throughput_item.setForeground(QColor(144, 238, 144))  # Light green
            elif throughput > 2:
                throughput_item.setForeground(QColor(173, 216, 230))  # Light blue
            
            self.summary_table.setItem(i, 0, model_item)
            self.summary_table.setItem(i, 1, tasks_item)
            self.summary_table.setItem(i, 2, time_item)
            self.summary_table.setItem(i, 3, throughput_item)
        
        # Auto-select last result
        if self.benchmark_results:
            self.summary_table.selectRow(len(self.benchmark_results) - 1)
            self.show_task_details(self.benchmark_results[-1])
    
    def show_task_details(self, results):
        self.results_table.setRowCount(len(results["results"]))
        
        for i, task in enumerate(results["results"]):
            # Truncate long prompts
            prompt_text = task["prompt"]
            if len(prompt_text) > 60:
                prompt_text = prompt_text[:57] + "..."
            
            prompt_item = QTableWidgetItem(prompt_text)
            prompt_item.setToolTip(task["prompt"])
            
            latency_item = QTableWidgetItem(f"{task['latency']:.4f}")
            latency_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            tokens_item = QTableWidgetItem(f"{task['tokens_sec']:.2f}")
            tokens_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Color code tokens/s for performance
            tokens_per_sec = task['tokens_sec']
            if tokens_per_sec > 60:
                tokens_item.setForeground(QColor(144, 238, 144))  # Light green
            elif tokens_per_sec > 30:
                tokens_item.setForeground(QColor(173, 216, 230))  # Light blue
            
            # Add status indicator
            status_item = QTableWidgetItem("✅ Success")
            status_item.setForeground(QColor(144, 238, 144))  # Green
            
            self.results_table.setItem(i, 0, prompt_item)
            self.results_table.setItem(i, 1, latency_item)
            self.results_table.setItem(i, 2, tokens_item)
            self.results_table.setItem(i, 3, status_item)
        
        # Add overall metrics row
        self.results_table.insertRow(0)
        
        avg_latency = sum(t["latency"] for t in results["results"]) / len(results["results"])
        avg_tokens = sum(t["tokens_sec"] for t in results["results"]) / len(results["results"])
        
        avg_latency_item = QTableWidgetItem(f"{avg_latency:.4f}")
        avg_latency_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        avg_latency_item.setBackground(QColor(70, 70, 70))
        
        avg_tokens_item = QTableWidgetItem(f"{avg_tokens:.2f}")
        avg_tokens_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        avg_tokens_item.setBackground(QColor(70, 70, 70))
        
        self.results_table.setItem(0, 0, QTableWidgetItem("AVERAGE"))
        self.results_table.setItem(0, 1, avg_latency_item)
        self.results_table.setItem(0, 2, avg_tokens_item)
        self.results_table.setItem(0, 3, QTableWidgetItem("Aggregate"))
        self.results_table.item(0, 0).setBackground(QColor(70, 70, 70))
        self.results_table.item(0, 3).setBackground(QColor(70, 70, 70))
    
    def closeEvent(self, event):
        if self.benchmark_worker and self.benchmark_worker.isRunning():
            self.benchmark_worker.cancel()
            self.benchmark_worker.terminate()
            self.benchmark_worker.wait(2000)
        
        # Save results to JSON
        if self.benchmark_results:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"ollama_concurrency_benchmark_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(self.benchmark_results, f, indent=2)
            print(f"Benchmark results saved to {filename}")
        
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setFont(QFont("Arial", 9))
    
    # Create and show main window
    window = OllamaBenchmarkApp()
    window.show()
    
    sys.exit(app.exec_())
