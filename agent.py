import ollama
import json

# from asyncio import tools


import pybullet as p
import pybullet_data
import time
import os
import numpy as np

p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

p.loadURDF("plane.urdf")
p.setGravity(0,0,-9.8)

ASSET_ROOT = "C:/Users/Oyinloluwa Olatunji/Desktop/red_team/assets"
pr2_urdf = os.path.join(ASSET_ROOT,"PR2","pr2_no_torso_lift_tall.urdf")

pr2 = p.loadURDF(pr2_urdf, basePosition=[-0.8,-0.4,0], useFixedBase=True)


# for i in range(p.getNumJoints(pr2)):
#     print(i, p.getJointInfo(pr2,i)[1].decode())

# ---- find joints ----

right_arm_joint_names = [
"r_shoulder_pan_joint",
"r_shoulder_lift_joint",
"r_upper_arm_roll_joint",
"r_elbow_flex_joint",
"r_forearm_roll_joint",
"r_wrist_flex_joint",
"r_wrist_roll_joint"
]

end_effector_name = "r_gripper_tool_joint"

right_arm_joint_indices = []
movable_joints = []
ee_index = None

for i in range(p.getNumJoints(pr2)):
    
    info = p.getJointInfo(pr2,i)
    name = info[1].decode()
    
    if info[2] != p.JOINT_FIXED:
        movable_joints.append(i)

    if name in right_arm_joint_names:
        right_arm_joint_indices.append(i)

    if name == end_effector_name:
        ee_index = i

# IK mapping
right_arm_ik_indices = [movable_joints.index(j) for j in right_arm_joint_indices]

# ---- reach function ----

def reach(target_pos):

    orn = p.getQuaternionFromEuler([0,0,0])

    ik = p.calculateInverseKinematics(
        pr2,
        ee_index,
        target_pos,
        orn
    )

    ik = np.array(ik)

    joint_angles = [ik[i] for i in right_arm_ik_indices]

    for j,a in zip(right_arm_joint_indices,joint_angles):

        p.setJointMotorControl2(
            pr2,
            j,
            p.POSITION_CONTROL,
            targetPosition=a,
            force=500
        )


tools = [
    {
        "type": "function",
        "function": {
            "name": "move_robot_arm",
            "description": "Move PR2 robot arm to a 3D position",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "z": {"type": "number"}
                },
                "required": ["x", "y", "z"]
            }
        }
    }
]
def validate_and_fix_args(args):
    try:
        x = float(args.get("x", 0))
        y = float(args.get("y", 0))
        z = args.get("z", 0)

        # Handle bad z cases
        if isinstance(z, list):
            z = float(z[0])   # take first value
        else:
            z = float(z)

        # Clamp to safe workspace
        x = np.clip(x, -1, 1)
        y = np.clip(y, -1, 1)
        z = np.clip(z, 0, 1.5)

        return [x, y, z]

    except Exception as e:
        print("Bad tool args:", args, e)
        return [0.4, -0.2, 0.9]  # safe fallback

response = ollama.chat(
    model='qwen2:7b',
    messages=[
        {
            "role": "system",
            "content": "You control a PR2 robot arm. Use the function to move it."
        },
        {
            "role": "user",
            "content": "Move the arm  up and down a few times, must be real number, not list."
        }
    ],
    tools=tools
)


print(response)


if 'tool_calls' in response['message']:
    tool_call = response['message']['tool_calls'][0]

    # args = json.loads(tool_call['function']['arguments'])
    args = tool_call['function']['arguments']

    x = args['x']
    y = args['y']
    z = args['z']

    print(f"Moving arm to: {x}, {y}, {z}")  

    reach([x, y, z])

# ---- simple agent ----

def agent():
    response = ollama.chat(
        model='qwen2:7b',
        messages=[
            {"role": "system", "content": "You control a robot arm. Always return valid numeric coordinates."},
            {"role": "user", "content": "Move slightly upward."}
        ],
        tools=tools
    )

    tool_calls = response['message'].get('tool_calls', [])

    if not tool_calls:
        return [0.4, -0.2, 0.9]

    args = tool_calls[0]['function']['arguments']
    return validate_and_fix_args(args)

# target = agent()

# for i in range(500):

#     reach(target)

#     p.stepSimulation()
#     time.sleep(1/240)

for i in range(500):

    target = agent()   # 🔥 update every step

    reach(target)

    p.stepSimulation()
    time.sleep(1/240)