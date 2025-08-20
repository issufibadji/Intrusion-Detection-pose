import cv2
from sort import *
import numpy as np
from tkinter import messagebox
import sys
from ultralytics import YOLO
import cvzone
from tkinter import *
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import threading
import numpy as np
from datetime import datetime

# Global variables
running = False
intrusion_detected = set()
video_path = None
polygon_file_path = None
# Function for intrusion detection
def load_polygon_coordinates(file_path):
    try:
        with open(file_path, 'r') as file:
            line = file.readline().strip()
            # Evaluate the np.array statement from the file
            coordinates = eval(line)
            if isinstance(coordinates, np.ndarray):
                return coordinates
            else:
                raise ValueError("The file does not contain a valid numpy array.")
            
    except Exception as e:
        print(f"Error reading polygon coordinates: {e}")
        return None

def intrusion_detection():
    global running, intrusion_detected

    # Check if files are selected
    if  not video_path and not polygon_file_path:
        messagebox.showerror("Error", "Please choose a video file and polygon coordinate txt file")
        return

    if not video_path:
        messagebox.showerror("Error", "Please choose a video file")
        return
    
    if not polygon_file_path:
        messagebox.showerror("Error", "Please choose a polygon coordinate file.")
        return
    
    polygon_coordinates = load_polygon_coordinates(polygon_file_path)

    if polygon_coordinates is not None:
        print("Loaded polygon coordinates:")
        print(polygon_coordinates)
    else:
        print("Failed to load polygon coordinates.")
        messagebox.showerror("Error", "not valid polygon coordinate")

    # Initialize video capture and YOLO model
    cap = cv2.VideoCapture(video_path)
    model = YOLO('yolov8n.pt')

    # Load class names
    classnames = []
    with open('classes.txt', 'r') as f:
        classnames = f.read().splitlines()

    # Initialize SORT tracker
    tracker = Sort(max_age=30)

    # Define the original region of interest (polygon region)
    original_frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    region_points = polygon_coordinates
    # Track objects that have entered the region
    intrusion_detected = set()

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize the frame for display in Tkinter
        display_width, display_height = 800, 450
        frame = cv2.resize(frame, (display_width, display_height))

        # Scale region points to match the resized frame
        scale_x = display_width / original_frame_width
        scale_y = display_height / original_frame_height
        scaled_region_points = np.array(
            [[int(pt[0] * scale_x), int(pt[1] * scale_y)] for pt in region_points],
            np.int32
        )

        detections = np.empty((0, 5))
        results = model(frame, stream=1)

        # Extract bounding boxes for "person" class
        for info in results:
            boxes = info.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                conf = box.conf[0]
                classindex = box.cls[0]
                object_detected = classnames[int(classindex)]

                if object_detected == 'person' and conf > 0.4:
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    new_detections = np.array([x1, y1, x2, y2, conf])
                    detections = np.vstack((detections, new_detections))

        # Update tracker
        track_result = tracker.update(detections)

        # Draw the polygon region
        cv2.polylines(frame, [scaled_region_points], isClosed=True, color=(0, 255, 255), thickness=2)

        # Set font properties for text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_thickness = 2
        color = (0,255,0)  # intrusion detected
        cv2.putText(frame, "Status: Monitoring", (20, 40), font, font_scale, (0, 255, 0), font_thickness)

        for result in track_result:
            x1, y1, x2, y2, obj_id = map(int, result)

            # Calculate the midpoint of the bounding box
            box_mid = ((x1 + x2) // 2, (y1 + y2) // 2)

            # Check if the midpoint of the tracked object is inside the polygon
            if cv2.pointPolygonTest(scaled_region_points, box_mid, False) >= 0 and obj_id not in intrusion_detected:
                intrusion_detected.add(obj_id)
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_intrusion(obj_id, box_mid,current_time)

                # Set font properties for text
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.7
                font_thickness = 2
                color = (0, 0, 255)  # intrusion detected
                cv2.putText(frame, "Status:Intrusion Detected", (20,40), font, font_scale, color, font_thickness)


            # Draw bounding box and object ID
            color = (0, 0, 255) if obj_id in intrusion_detected else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cvzone.putTextRect(frame, f'ID: {obj_id}', [x1 + 5, y1 - 10], thickness=1, scale=1.2)

        # Convert frame to ImageTk format for Tkinter
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        try:

            imgtk = ImageTk.PhotoImage(image=img)

            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)
            root.update()
        except:
            pass
    cap.release()
    cv2.destroyAllWindows()

# Function to log intrusions
def log_intrusion(obj_id, position,date_time_info):
    intrusion_list.insert("", "end", values=(obj_id, position,date_time_info))
    intrusion_count.set(len(intrusion_detected))

# Function to start the intrusion detection thread
def start_intrusion_detection():
    global running
    running = True
    threading.Thread(target=intrusion_detection).start()

# Function to stop intrusion detection
def stop_intrusion_detection():
    global running
    running = False
    sys.exit(1)

# Function to choose video file
def choose_video_file():
    global video_path
    file_path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=(("MP4 Files", "*.mp4"), ("All Files", "*.*"))
    )
    if file_path:
        video_path = file_path

# Function to choose video file
def choose_polygon_txt_file():
    global polygon_file_path
    polygon_file_path = filedialog.askopenfilename(
        title="Select txt File which contains polygon coordinate with array format",
        filetypes=(("txt Files", "*.txt"), ("All Files", "*.*"))
    )
    if polygon_file_path:
        polygon_file_path = polygon_file_path

# Initialize Tkinter window
root = Tk()
root.title("Intrusion Detection System")
root.geometry("1024x600")
root.resizable(True, True)

# Style configuration
style = ttk.Style()
style.configure("TNotebook.Tab", font=("Arial", 12))
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
style.configure("Treeview", font=("Arial", 10))

# Tabbed interface
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Video tab
video_frame = Frame(notebook, bg="black")
notebook.add(video_frame, text="Live Video")

# Intrusion log tab
log_frame = Frame(notebook)
notebook.add(log_frame, text="Intrusion Log")

# Video frame title label
title_label = Label(video_frame, text="Intrusion Detection System", font=("Arial", 18, "bold"), bg="black", fg="white")
title_label.pack(fill="x", pady=10)  # Add some padding to create space above the video

# Video display label
video_label = Label(video_frame, bg="black")
video_label.pack(fill="both", expand=True, padx=10, pady=10)

# Intrusion count label
intrusion_count = IntVar(value=0)
count_frame = Frame(video_frame, bg="black")
count_frame.pack(pady=10)
Label(count_frame, text="Intrusions Detected:", font=("Arial", 14), bg="black", fg="white").pack(side="left", padx=5)
Label(count_frame, textvariable=intrusion_count, font=("Arial", 14), bg="black", fg="red").pack(side="left")

# Intrusion log table
columns = ("Object ID", "Position","Date & Time")
intrusion_list = ttk.Treeview(log_frame, columns=columns, show="headings", height=15)
intrusion_list.heading("Object ID", text="Object ID")
intrusion_list.heading("Position", text="Position")
intrusion_list.heading("Date & Time", text="Date & Time")
intrusion_list.pack(fill="both", expand=True, padx=10, pady=10)

# Control buttons
button_frame = Frame(root)
button_frame.pack(fill="x", pady=5)

choose_button = Button(button_frame, text="Choose Video File", command=choose_video_file, font=("Arial", 12), bg="blue", fg="white")
choose_button.pack(side="left", padx=10)

choose_button = Button(button_frame, text="Choose polygon coordinate txt file",command=choose_polygon_txt_file, font=("Arial", 12), bg="blue", fg="white")
choose_button.pack(side="left", padx=10)

start_button = Button(button_frame, text="Start", command=start_intrusion_detection, font=("Arial", 12), bg="green", fg="white")
start_button.pack(side="left", padx=10)

stop_button = Button(button_frame, text="Stop", command=stop_intrusion_detection, font=("Arial", 12), bg="red", fg="white")
stop_button.pack(side="left", padx=10)

# Start the Tkinter main loop
root.mainloop()
