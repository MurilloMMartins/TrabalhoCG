import glm
import math

class Camera:
    def __init__(self, mouse_sensitivity, camera_speed) -> None:
        self.position = glm.vec3(0.0, 0.0, 1.0)
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.mouse_sensitivity = mouse_sensitivity
        self.speed = camera_speed
        self.pitch = 0.0
        self.yaw = -90.0

    def set_position(self, new_position: glm.vec3):
        # Stop camera from leaving the skybox
        new_position.x = min(max(new_position.x, -400), 400)
        new_position.y = min(max(new_position.y, -2), 400)
        new_position.z = min(max(new_position.z, -400), 400)

        self.position = new_position

    def look_at(self):
        return glm.lookAt(self.position, self.position + self.front, self.up)
    
    def update_front(self, xoffset, yoffset):
        xoffset *= self.mouse_sensitivity
        yoffset *= self.mouse_sensitivity

        self.yaw += xoffset;
        self.pitch += yoffset;
        
        if self.pitch >= 90.0: 
            self.pitch = 90.0
        if self.pitch <= -90.0: 
            self.pitch = -90.0

        new_front = glm.vec3()
        new_front.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        new_front.y = math.sin(glm.radians(self.pitch))
        new_front.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))

        # Prevent division by 0
        if abs(new_front.y) <= 0.001: new_front.y = 0.001
        if abs(new_front.z) <= 0.001: new_front.z = 0.001
        if abs(new_front.x) <= 0.001: new_front.x = 0.001

        self.front = glm.normalize(new_front)
