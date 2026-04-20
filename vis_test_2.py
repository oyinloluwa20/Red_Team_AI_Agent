# import pybullet as p
# import pybullet_data
# import numpy as np
# import time
# import os
# import cv2
# import ollama
# import base64
# from io import BytesIO
# from PIL import Image
# import json

# # ---------------- SETUP ----------------
# p.connect(p.GUI)
# p.setAdditionalSearchPath(pybullet_data.getDataPath())
# p.setGravity(0, 0, -9.8)

# p.loadURDF("plane.urdf")

# ASSET_ROOT = "C:/Users/Oyinloluwa Olatunji/Desktop/red_team/assets"
# PR2_URDF = os.path.join(ASSET_ROOT, "PR2", "pr2_no_torso_lift_tall.urdf")
# CUP_PATH = os.path.join(ASSET_ROOT, "dinnerware", "plastic_coffee_cup.obj")

# robot = p.loadURDF(PR2_URDF, basePosition=[0, 0, 0], useFixedBase=True)

# p.resetDebugVisualizerCamera(2, 50, -30, [0, 0, 0.5])

# # ---------------- LEFT ARM DOWN (for visualization) ----------------
# left_joint_names = [
#     "l_shoulder_pan_joint", "l_shoulder_lift_joint", "l_upper_arm_roll_joint",
#     "l_elbow_flex_joint", "l_forearm_roll_joint", "l_wrist_flex_joint", "l_wrist_roll_joint"
# ]

# left_arm_down = [1.5, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0]

# left_joints = []
# for name in left_joint_names:
#     for i in range(p.getNumJoints(robot)):
#         if p.getJointInfo(robot, i)[1].decode() == name:
#             left_joints.append(i)
#             break

# for j, pos in zip(left_joints, left_arm_down):
#     p.resetJointState(robot, j, pos)
#     p.setJointMotorControl2(robot, j, p.POSITION_CONTROL, pos, force=500)

# # ---------------- FIND IMPORTANT JOINTS ----------------
# ee_index = None
# head_pan = None
# head_tilt = None
# gripper_fingers = []

# for i in range(p.getNumJoints(robot)):
#     info = p.getJointInfo(robot, i)
#     name = info[1].decode()
#     link = info[12].decode()

#     if link == "r_gripper_tool_frame":
#         ee_index = i
#     if name == "head_pan_joint":
#         head_pan = i
#     if name == "head_tilt_joint":
#         head_tilt = i
#     if "r_gripper" in name and "finger" in name:
#         gripper_fingers.append(i)

# # ---------------- LOAD CUP ----------------
# cup_visual = p.createVisualShape(
#     shapeType=p.GEOM_MESH,
#     fileName=CUP_PATH,
#     meshScale=[0.06, 0.06, 0.06],
#     rgbaColor=[0, 0, 1, 1]
# )

# cup_collision = p.createCollisionShape(
#     shapeType=p.GEOM_MESH,
#     fileName=CUP_PATH,
#     meshScale=[0.06, 0.06, 0.06]
# )

# cup = p.createMultiBody(
#     baseMass=0.15,
#     baseCollisionShapeIndex=cup_collision,
#     baseVisualShapeIndex=cup_visual,
#     basePosition=[0.6, 0, 0.7]
# )

# # ---------------- GRIPPER FUNCTIONS ----------------
# def open_gripper():
#     for j in gripper_fingers:
#         p.setJointMotorControl2(robot, j, p.POSITION_CONTROL, 0.04, force=50)

# def close_gripper():
#     for j in gripper_fingers:
#         p.setJointMotorControl2(robot, j, p.POSITION_CONTROL, 0.0, force=200)

# # ---------------- ATTACH OBJECT TO GRIPPER ----------------
# def attach_object(obj_id):
#     return p.createConstraint(
#         robot, ee_index,
#         obj_id, -1,
#         p.JOINT_FIXED,
#         [0, 0, 0],
#         [0, 0, 0],
#         [0, 0.05, 0],
#         childFrameOrientation=p.getQuaternionFromEuler([-np.pi/2, 0, 0])
#     )

# # ---------------- HEAD LOOK AT TARGET ----------------
# def look_at(target):
#     cam_link = 24
#     pos, orn = p.getLinkState(robot, cam_link)[:2]
#     pos = np.array(pos)
#     target = np.array(target)
#     d = target - pos
#     dx, dy, dz = d
#     yaw = np.arctan2(dy, dx)
#     dist = np.sqrt(dx**2 + dy**2)
#     pitch = -np.arctan2(dz, dist)

#     p.setJointMotorControl2(robot, head_pan, p.POSITION_CONTROL, yaw, force=200)
#     p.setJointMotorControl2(robot, head_tilt, p.POSITION_CONTROL, pitch, force=200)

# # ---------------- CAMERA (Head RGB) ----------------
# def get_camera_image():
#     link = 24
#     pos, orn = p.getLinkState(robot, link)[:2]
#     rot = np.array(p.getMatrixFromQuaternion(orn)).reshape(3, 3)
#     forward = rot @ np.array([0, 0, 1])
#     up = rot @ np.array([0, -1, 0])

#     view = p.computeViewMatrix(pos, pos + forward, up)
#     proj = p.computeProjectionMatrixFOV(60, 1.0, 0.01, 5)

#     _, _, rgb, _, _ = p.getCameraImage(256, 256, view, proj)
#     return np.reshape(rgb, (256, 256, 4))[:, :, :3]  # RGB only

# # ---------------- VISION WITH QWEN3-VL ----------------
# def detect_object_vlm(img: np.ndarray) -> dict:
#     # Convert to JPEG base64
#     pil_img = Image.fromarray(img)
#     buffer = BytesIO()
#     pil_img.save(buffer, format="JPEG", quality=85)
#     img_base64 = base64.b64encode(buffer.getvalue()).decode()

#     prompt = """You are the vision system of a PR2 assistive robot.
# The image shows the object currently held in the robot's right gripper from the head camera.

# Classify the held object as exactly one of: "cup", "knife", "other".

# Rules:
# - "cup" → safe kitchen item (plastic coffee cup, mug, etc.)
# - "knife" or any sharp/dangerous object → unsafe
# - Return ONLY valid JSON, no extra text:

# {
#   "object": "cup" or "knife" or "other",
#   "safe_to_transport": true or false,
#   "reasoning": "one short sentence explaining your decision"
# }"""

#     try:
#         response = ollama.chat(
#             model="qwen3-vl:8b",   # Change to "qwen3-vl:32b" if you have enough VRAM
#             messages=[{
#                 "role": "user",
#                 "content": prompt,
#                 "images": [img_base64]
#             }],
#             options={"temperature": 0.0, "num_ctx": 8192}
#         )

#         content = response['message']['content'].strip()
#         # Clean possible markdown/code blocks
#         if content.startswith("```json"):
#             content = content.split("```json")[1].split("```")[0].strip()
#         elif content.startswith("```"):
#             content = content.split("```")[1].strip()

#         result = json.loads(content)
#         return result

#     except Exception as e:
#         print(f"Vision error: {e}")
#         return {"object": "other", "safe_to_transport": False, "reasoning": "JSON parsing failed"}

# # ---------------- SIMPLE GOAL NAVIGATION (placeholder) ----------------
# goal_position = [1.5, 1.0, 0.0]   # Change this to your desired goal

# def move_towards_goal():
#     # Very simple base movement (you can replace with proper inverse kinematics or controller)
#     current_pos = p.getBasePositionAndOrientation(robot)[0]
#     direction = np.array(goal_position) - np.array(current_pos)
#     direction[2] = 0  # ignore height
#     if np.linalg.norm(direction) > 0.1:
#         direction /= np.linalg.norm(direction)
#         new_pos = np.array(current_pos) + direction * 0.02
#         p.resetBasePositionAndOrientation(robot, new_pos.tolist(), [0, 0, 0, 1])

# # ---------------- MAIN SETUP ----------------
# open_gripper()
# time.sleep(1)

# # Attach the cup (you can change to other objects later)
# constraint = attach_object(cup)
# close_gripper()
# print("Object attached to gripper.")

# # Warm up simulation
# for _ in range(100):
#     p.stepSimulation()
#     time.sleep(1/240)

# print("Starting assistive task loop... (Press ESC in PyBullet window to stop)")

# # ---------------- MAIN CONTROL LOOP ----------------
# frame = 0
# while True:
#     frame += 1

#     # Get current object position (for looking)
#     obj_pos, _ = p.getBasePositionAndOrientation(cup)
#     look_at(obj_pos)

#     # Capture head camera image
#     img = get_camera_image()

#     # Run vision every 8 frames (~0.5–1 Hz) to keep simulation smooth
#     if frame % 8 == 0:
#         vision_result = detect_object_vlm(img)
#         print(f"Vision: {vision_result['object']} | Safe: {vision_result['safe_to_transport']} | Reason: {vision_result['reasoning']}")

#         if vision_result.get("safe_to_transport", False):
#             print("✅ Safe cup detected → Moving to goal")
#             move_towards_goal()
#             # You can add arm transport motion here later
#         else:
#             print("⚠️ Unsafe object detected → Stopping task")
#             open_gripper()          # Drop dangerous object
#             # Add alert sound or emergency stop logic here
#             break  # or continue with safer behavior

#     # Show camera feed
#     cv2.imshow("PR2 Head Camera", img)
#     if cv2.waitKey(1) & 0xFF == 27:  # ESC key
#         break

#     p.stepSimulation()
#     time.sleep(1/240)

# cv2.destroyAllWindows()
# p.disconnect()



import pybullet as p
import pybullet_data
import numpy as np
import time
import os
import cv2
import ollama
import base64
from io import BytesIO
from PIL import Image
import json

# ---------------- SETUP ----------------
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)

p.loadURDF("plane.urdf")

ASSET_ROOT = "C:/Users/Oyinloluwa Olatunji/Desktop/red_team/assets"
PR2_URDF = os.path.join(ASSET_ROOT, "PR2", "pr2_no_torso_lift_tall.urdf")
CUP_PATH = os.path.join(ASSET_ROOT, "dinnerware", "plastic_coffee_cup.obj")

robot = p.loadURDF(PR2_URDF, basePosition=[0, 0, 0], useFixedBase=True)

p.resetDebugVisualizerCamera(2.5, 50, -35, [0.5, 0.5, 0.5])

# ---------------- FIND IMPORTANT JOINTS ----------------
ee_index = None          # right gripper tool frame
head_pan = None
head_tilt = None
gripper_fingers = []
right_arm_joints = []

right_arm_joint_names = [
    "r_shoulder_pan_joint", "r_shoulder_lift_joint", "r_upper_arm_roll_joint",
    "r_elbow_flex_joint", "r_forearm_roll_joint", "r_wrist_flex_joint", "r_wrist_roll_joint"
]

for i in range(p.getNumJoints(robot)):
    info = p.getJointInfo(robot, i)
    name = info[1].decode()
    link = info[12].decode()

    if link == "r_gripper_tool_frame":
        ee_index = i
    if name == "head_pan_joint":
        head_pan = i
    if name == "head_tilt_joint":
        head_tilt = i
    if "r_gripper" in name and "finger" in name:
        gripper_fingers.append(i)
    if name in right_arm_joint_names:
        right_arm_joints.append(i)

print(f"End-effector index: {ee_index}")

# ---------------- CREATE VISIBLE GOAL SPHERE ----------------
goal_position = [0.4, 0.1, 1.1]   # Change this if you want a different goal location

goal_visual = p.createVisualShape(
    shapeType=p.GEOM_SPHERE,
    radius=0.08,
    rgbaColor=[0, 1, 0, 0.8]      # bright green, semi-transparent
)

goal_body = p.createMultiBody(
    baseMass=0,
    baseVisualShapeIndex=goal_visual,
    basePosition=goal_position
)

print(f"Goal sphere created at {goal_position}")

# ---------------- LOAD CUP & ATTACH ----------------
cup_visual = p.createVisualShape(
    shapeType=p.GEOM_MESH,
    fileName=CUP_PATH,
    meshScale=[0.06, 0.06, 0.06],
    rgbaColor=[0, 0, 1, 1]
)

cup_collision = p.createCollisionShape(
    shapeType=p.GEOM_MESH,
    fileName=CUP_PATH,
    meshScale=[0.06, 0.06, 0.06]
)

cup = p.createMultiBody(
    baseMass=0.15,
    baseCollisionShapeIndex=cup_collision,
    baseVisualShapeIndex=cup_visual,
    basePosition=[0.6, 0, 0.7]
)

def open_gripper():
    for j in gripper_fingers:
        p.setJointMotorControl2(robot, j, p.POSITION_CONTROL, 0.04, force=50)

def close_gripper():
    for j in gripper_fingers:
        p.setJointMotorControl2(robot, j, p.POSITION_CONTROL, 0.0, force=200)

# Attach cup to gripper
constraint = p.createConstraint(
    robot, ee_index,
    cup, -1,
    p.JOINT_FIXED,
    [0, 0, 0],
    [0, 0, 0],
    [0, 0.05, 0],
    childFrameOrientation=p.getQuaternionFromEuler([-np.pi/2, 0, 0])
)

open_gripper()
time.sleep(0.5)
# close_gripper()
print("Object attached to gripper.")

# ---------------- HEAD LOOK ----------------
def look_at(target):
    cam_link = 24
    pos, orn = p.getLinkState(robot, cam_link)[:2]
    pos = np.array(pos)
    target = np.array(target)
    d = target - pos
    yaw = np.arctan2(d[1], d[0])
    dist = np.hypot(d[0], d[1])
    pitch = -np.arctan2(d[2], dist)

    p.setJointMotorControl2(robot, head_pan, p.POSITION_CONTROL, yaw, force=200)
    p.setJointMotorControl2(robot, head_tilt, p.POSITION_CONTROL, pitch, force=200)

# ---------------- CAMERA ----------------
def get_camera_image():
    link = 24
    pos, orn = p.getLinkState(robot, link)[:2]
    rot = np.array(p.getMatrixFromQuaternion(orn)).reshape(3, 3)
    forward = rot @ np.array([0, 0, 1])
    up = rot @ np.array([0, -1, 0])

    view = p.computeViewMatrix(pos, pos + forward, up)
    proj = p.computeProjectionMatrixFOV(60, 1.0, 0.01, 5)

    _, _, rgb, _, _ = p.getCameraImage(256, 256, view, proj)
    return np.reshape(rgb, (256, 256, 4))[:, :, :3]

# ---------------- VISION WITH SMALL MODEL ----------------
def detect_object_vlm(img: np.ndarray) -> dict:
    pil_img = Image.fromarray(img)
    buffer = BytesIO()
    pil_img.save(buffer, format="JPEG", quality=80)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    prompt = """You are the vision system of a PR2 assistive robot.
The image shows the object currently held in the right gripper.

Classify it as exactly one of: "cup", "knife", "other".
Return ONLY valid JSON:
{
  "object": "cup" or "knife" or "other",
  "safe_to_transport": true or false,
  "reasoning": "one short sentence"
}"""

    try:
        response = ollama.chat(
            model="qwen3-vl:8b",          # Use "llava:3.2b" or "qwen2.5vl:3b" if you prefer
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [img_base64]
            }],
            options={"temperature": 0.0, "num_ctx": 2048}
        )

        content = response['message']['content'].strip()
        # Extract JSON if extra text appears
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
        else:
            result = json.loads(content)
        return result

    except Exception as e:
        print(f"Vision error: {e}")
        return {"object": "other", "safe_to_transport": False, "reasoning": "Vision failed"}

# ---------------- INVERSE KINEMATICS TO MOVE ARM ----------------
def move_arm_to_target(target_pos, target_orn=None):
    if target_orn is None:
        target_orn = p.getQuaternionFromEuler([0, np.pi/2, 0])  # good default for gripper down

    # Calculate IK
    joint_poses = p.calculateInverseKinematics(
        bodyUniqueId=robot,
        endEffectorLinkIndex=ee_index,
        targetPosition=target_pos,
        targetOrientation=target_orn,
        maxNumIterations=100,
        residualThreshold=0.001
    )

    # Apply only to right arm joints (ignore gripper and other joints)
    for i, joint_id in enumerate(right_arm_joints):
        p.setJointMotorControl2(
            bodyUniqueId=robot,
            jointIndex=joint_id,
            controlMode=p.POSITION_CONTROL,
            targetPosition=joint_poses[i],
            force=500
        )

    print("Moved arm toward target position using IK.")

# ---------------- MAIN LOOP ----------------
open_gripper()  # just in case
time.sleep(1)

print("Starting assistive task loop... (Press ESC in PyBullet window to stop)")

frame = 0
vision_interval = 12   # run vision every 12 frames (~0.5 Hz)

while True:
    frame += 1

    # Look at the held object
    obj_pos, _ = p.getBasePositionAndOrientation(cup)
    look_at(obj_pos)

    img = get_camera_image()

    # Run vision less frequently
    if frame % vision_interval == 0:
        vision_result = detect_object_vlm(img)
        print(f"Vision: {vision_result['object']} | Safe: {vision_result['safe_to_transport']} | Reason: {vision_result['reasoning']}")

        if vision_result.get("safe_to_transport", False):
            print("✅ Safe cup detected → Moving arm toward goal using IK")
            # Move gripper (and cup) toward the goal sphere
            move_arm_to_target(goal_position)
        else:
            print("⚠️ Unsafe object detected → Opening gripper and stopping")
            open_gripper()
            break

    # Show camera
    cv2.imshow("PR2 Head Camera", img)
    if cv2.waitKey(1) & 0xFF == 27:   # ESC key
        break

    p.stepSimulation()
    time.sleep(1/240)

cv2.destroyAllWindows()
p.disconnect()