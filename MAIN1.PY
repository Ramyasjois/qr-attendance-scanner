import cv2
from pyzbar.pyzbar import decode
import datetime
import numpy as np  # Import NumPy

# Define a list of valid QR code data
VALID_QR_CODES = {"1tj22cs403", "1TJ22CS407" "ABCDEF123456", "SOMEVALIDCODE"}

# Create a dictionary to store logged QR codes with dates
daily_logged_qr_codes = {}


def log_attendance(data, status):
    # Open the attendance file in append mode
    with open("attendance.txt", "a") as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} - {data} - {status}\n")
    print(f"Logged {status} for: {data}")


def get_today_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def main():
    # Initialize the webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Scanning QR codes for attendance...")

    # Get today's date
    today_date = get_today_date()

    # Initialize daily logged QR codes for today
    if today_date not in daily_logged_qr_codes:
        daily_logged_qr_codes[today_date] = set()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        # Decode QR codes
        decoded_objects = decode(frame)

        for obj in decoded_objects:
            # Extract QR code data
            qr_data = obj.data.decode("utf-8").strip()  # Strip extra whitespace
            print(f"Detected QR code data: '{qr_data}'")  # Debug print
            status = "Denied"

            # Check if QR code is in the valid list
            if qr_data in VALID_QR_CODES:
                if qr_data not in daily_logged_qr_codes[today_date]:
                    # Set status to "Granted" if valid and not previously logged today
                    status = "Granted"
                    # Log attendance
                    log_attendance(qr_data, status)
                    # Mark this QR code as logged for today
                    daily_logged_qr_codes[today_date].add(qr_data)
                else:
                    # Log denial if already logged today
                    status = "Already Logged Today"
            else:
                # Log denial if not valid
                status = "Denied"

            # Draw rectangle around the QR code
            points = obj.polygon
            if len(points) == 4:
                cv2.polylines(frame, [np.array(points, dtype=np.int32)], True, (0, 255, 0), 2)

            # Display status message
            color = (0, 255, 0) if status == "Granted" else (0, 0, 255) if status == "Denied" else (255, 255, 0)
            cv2.putText(frame, status, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame, qr_data, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 1)

        # Display the frame
        cv2.imshow('QR Code Scanner', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
