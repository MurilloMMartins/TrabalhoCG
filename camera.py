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
        self.front = glm.normalize(new_front)