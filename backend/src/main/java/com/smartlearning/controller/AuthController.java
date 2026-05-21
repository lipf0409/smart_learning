package com.smartlearning.controller;

import com.smartlearning.entity.User;
import com.smartlearning.repository.UserRepository;
import com.smartlearning.service.PasswordService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordService passwordService;

    @PostMapping("/register")
    public ResponseEntity<Map<String, Object>> register(@RequestBody Map<String, String> request) {
        String username = request.get("username");
        String password = request.get("password");
        String email = request.get("email");

        Map<String, Object> response = new HashMap<>();

        // 参数校验
        if (username == null || username.trim().isEmpty()) {
            response.put("success", false);
            response.put("message", "用户名不能为空");
            return ResponseEntity.badRequest().body(response);
        }

        if (password == null || password.length() < 6) {
            response.put("success", false);
            response.put("message", "密码长度至少6位");
            return ResponseEntity.badRequest().body(response);
        }

        // 检查用户名是否已存在
        if (userRepository.existsByUsername(username)) {
            response.put("success", false);
            response.put("message", "用户名已存在");
            return ResponseEntity.badRequest().body(response);
        }

        // 检查邮箱是否已被使用
        if (email != null && !email.isEmpty() && userRepository.existsByEmail(email)) {
            response.put("success", false);
            response.put("message", "邮箱已被注册");
            return ResponseEntity.badRequest().body(response);
        }

        // 创建用户并加密密码
        User user = new User();
        user.setUsername(username);
        user.setPassword(passwordService.encode(password)); // 使用 bcrypt 加密
        user.setEmail(email);
        userRepository.save(user);

        response.put("success", true);
        response.put("message", "注册成功");
        return ResponseEntity.ok(response);
    }

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody Map<String, String> request) {
        String username = request.get("username");
        String password = request.get("password");

        Map<String, Object> response = new HashMap<>();

        // 参数校验
        if (username == null || username.trim().isEmpty()) {
            response.put("success", false);
            response.put("message", "用户名不能为空");
            return ResponseEntity.badRequest().body(response);
        }

        if (password == null || password.isEmpty()) {
            response.put("success", false);
            response.put("message", "密码不能为空");
            return ResponseEntity.badRequest().body(response);
        }

        // 查找用户
        Optional<User> userOpt = userRepository.findByUsername(username);

        if (userOpt.isEmpty()) {
            response.put("success", false);
            response.put("message", "用户名或密码错误");
            return ResponseEntity.badRequest().body(response);
        }

        User user = userOpt.get();

        // 检查用户状态
        if ("disabled".equals(user.getStatus())) {
            response.put("success", false);
            response.put("message", "账号已被禁用，请联系管理员");
            return ResponseEntity.badRequest().body(response);
        }

        // 验证密码（使用 bcrypt）
        if (!passwordService.matches(password, user.getPassword())) {
            response.put("success", false);
            response.put("message", "用户名或密码错误");
            return ResponseEntity.badRequest().body(response);
        }

        // 生成 token（实际项目中应使用 JWT）
        String token = "token-" + System.currentTimeMillis() + "-" + user.getId();

        response.put("success", true);
        response.put("token", token);
        response.put("username", username);
        response.put("role", user.getRole());
        return ResponseEntity.ok(response);
    }

    @PostMapping("/logout")
    public ResponseEntity<Map<String, Object>> logout() {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "登出成功");
        return ResponseEntity.ok(response);
    }

    @PostMapping("/change-password")
    public ResponseEntity<Map<String, Object>> changePassword(@RequestBody Map<String, String> request) {
        String username = request.get("username");
        String oldPassword = request.get("oldPassword");
        String newPassword = request.get("newPassword");

        Map<String, Object> response = new HashMap<>();

        if (username == null || oldPassword == null || newPassword == null) {
            response.put("success", false);
            response.put("message", "参数不完整");
            return ResponseEntity.badRequest().body(response);
        }

        if (newPassword.length() < 6) {
            response.put("success", false);
            response.put("message", "新密码长度至少6位");
            return ResponseEntity.badRequest().body(response);
        }

        Optional<User> userOpt = userRepository.findByUsername(username);

        if (userOpt.isEmpty()) {
            response.put("success", false);
            response.put("message", "用户不存在");
            return ResponseEntity.badRequest().body(response);
        }

        User user = userOpt.get();

        // 验证旧密码
        if (!passwordService.matches(oldPassword, user.getPassword())) {
            response.put("success", false);
            response.put("message", "原密码错误");
            return ResponseEntity.badRequest().body(response);
        }

        // 更新密码
        user.setPassword(passwordService.encode(newPassword));
        userRepository.save(user);

        response.put("success", true);
        response.put("message", "密码修改成功");
        return ResponseEntity.ok(response);
    }
}
