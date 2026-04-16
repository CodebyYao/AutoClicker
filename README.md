# AutoClicker

---

## Introduction
A simple compiler built with PyAutoGUI that lets you build programs to control mouse movement and keyboard functions. \
A Scratch-like editor is provided for programming your button logic sequence.

---

## Environment Setup
```bash
# Create environment
conda create -n auto_clicker python=3.10
conda activate auto_clicker
pip install -r requirements.txt
```
---
## Launching the Program
```bash
# Activate Environment
conda activate auto_clicker

# Launch the GUI
cd Cropping_component
python real_time_complier.py
```
---

## Usage
### 1. Select Script
Enter the script name you want to alter or execute, and press submit.


<img src="assets/script_name.png" alt="Enter Script">

### 2. Add Components
Add components by clicking on the elements in the sidebar. Alter their sequence by dragging them around.


<img src="assets/script_sidebar.png" alt="Click side bar">

### 3. Edit Attributes
Edit the components' attributes by clicking on the elements and hitting update.


<img src="assets/script_attr.png" alt="Edit component">

### 4. Delete Components
Delete components by dragging them into the red bounding box.


<img src="assets/script_delete.png" alt="Delete component" height="200">

### 5. Run Execution
Save the script and click 'Run Script' to start execution.


<img src="assets/script_run.png" alt="Save Script" height="300">

---

## Script Example
Below is a simple demo script that searches for the YouTube icon on the screen and attempts to click it five times in a row.

```bash
# Activate Environment
conda activate auto_clicker

# Launch the GUI
cd Cropping_component
python real_time_complier.py
```

### 1. Load Demo
Enter 'Demo' into the script name field.


<img src="assets/click_demo.png" alt="Enter Demo">

### 2. Execute
Click 'Run Script'.

<img src="assets/script_run.png" alt="Save Script" height="300">

---
## Advanced Features
Because the script is saved in a human-readable list format, it is possible to use AI to generate scripts automatically. However, manual labor may still be required to select and capture the necessary screen images.