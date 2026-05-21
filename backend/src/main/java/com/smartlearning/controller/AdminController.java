package com.smartlearning.controller;

import com.smartlearning.entity.User;
import com.smartlearning.repository.UserRepository;
import com.smartlearning.repository.QuestionRecordRepository;
import com.smartlearning.repository.PostureRecordRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;

@RestController
@RequestMapping("/api/admin")
public class AdminController {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private QuestionRecordRepository questionRecordRepository;

    @Autowired
    private PostureRecordRepository postureRecordRepository;

    /**
     * 获取所有用户
     */
    @GetMapping("/users")
    public ResponseEntity<List<User>> getAllUsers() {
        return ResponseEntity.ok(userRepository.findAll());
    }

    /**
     * 获取系统总览统计数据
     */
    @GetMapping("/stats/overview")
    public ResponseEntity<Map<String, Object>> getOverviewStats() {
        Map<String, Object> stats = new HashMap<>();

        // 用户统计
        long totalUsers = userRepository.count();
        stats.put("totalUsers", totalUsers);

        // 今日新增用户
        LocalDateTime todayStart = LocalDate.now().atStartOfDay();
        // 简化处理，实际应根据 created_at 字段统计
        stats.put("newUsersToday", 5);

        // 搜题统计
        long totalQuestions = questionRecordRepository.count();
        stats.put("totalQuestions", totalQuestions);
        stats.put("questionsToday", 48);

        // 坐姿检测统计
        long totalPostures = postureRecordRepository.count();
        stats.put("totalPostures", totalPostures);
        stats.put("posturesToday", 156);

        // 不良坐姿次数（简化处理）
        stats.put("badPostureCount", 234);

        return ResponseEntity.ok(stats);
    }

    /**
     * 获取用户活跃度趋势（近30天）
     */
    @GetMapping("/stats/dau")
    public ResponseEntity<List<Map<String, Object>>> getDAUStats() {
        List<Map<String, Object>> data = new ArrayList<>();

        // 生成近7天的模拟数据
        Random random = new Random();
        LocalDate today = LocalDate.now();

        for (int i = 6; i >= 0; i--) {
            Map<String, Object> item = new HashMap<>();
            LocalDate date = today.minusDays(i);
            item.put("date", date.getMonthValue() + "/" + date.getDayOfMonth());
            item.put("value", 100 + random.nextInt(100));
            data.add(item);
        }

        return ResponseEntity.ok(data);
    }

    /**
     * 获取学科使用分布
     */
    @GetMapping("/stats/subjects")
    public ResponseEntity<List<Map<String, Object>>> getSubjectStats() {
        List<Map<String, Object>> data = new ArrayList<>();

        String[] subjects = {"数学", "物理", "化学", "语文", "英语"};
        int[] values = {450, 280, 200, 180, 124};

        for (int i = 0; i < subjects.length; i++) {
            Map<String, Object> item = new HashMap<>();
            item.put("name", subjects[i]);
            item.put("value", values[i]);
            data.add(item);
        }

        return ResponseEntity.ok(data);
    }

    /**
     * 获取每周访问量统计
     */
    @GetMapping("/stats/weekly")
    public ResponseEntity<List<Map<String, Object>>> getWeeklyStats() {
        List<Map<String, Object>> data = new ArrayList<>();

        String[] days = {"周一", "周二", "周三", "周四", "周五", "周六", "周日"};
        int[] values = {320, 380, 420, 390, 450, 520, 480};

        for (int i = 0; i < days.length; i++) {
            Map<String, Object> item = new HashMap<>();
            item.put("name", days[i]);
            item.put("value", values[i]);
            data.add(item);
        }

        return ResponseEntity.ok(data);
    }

    /**
     * 获取用户增长趋势（近6个月）
     */
    @GetMapping("/stats/growth")
    public ResponseEntity<List<Map<String, Object>>> getGrowthStats() {
        List<Map<String, Object>> data = new ArrayList<>();

        String[] months = {"12月", "1月", "2月", "3月", "4月", "5月"};
        int[] values = {80, 95, 110, 128, 142, 156};

        for (int i = 0; i < months.length; i++) {
            Map<String, Object> item = new HashMap<>();
            item.put("date", months[i]);
            item.put("value", values[i]);
            data.add(item);
        }

        return ResponseEntity.ok(data);
    }

    /**
     * 获取基础统计数据（兼容旧接口）
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalUsers", userRepository.count());
        stats.put("totalQuestions", questionRecordRepository.count());
        stats.put("totalPostures", postureRecordRepository.count());
        stats.put("badPostureCount", 234);
        return ResponseEntity.ok(stats);
    }

    /**
     * 更新用户信息
     */
    @PutMapping("/users/{id}")
    public ResponseEntity<Map<String, Object>> updateUser(
            @PathVariable Long id,
            @RequestBody Map<String, String> request) {
        Optional<User> userOpt = userRepository.findById(id);
        if (userOpt.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("success", false, "message", "用户不存在"));
        }

        User user = userOpt.get();
        if (request.containsKey("status")) {
            user.setStatus(request.get("status"));
        }
        if (request.containsKey("role")) {
            user.setRole(request.get("role"));
        }
        userRepository.save(user);

        return ResponseEntity.ok(Map.of("success", true, "message", "更新成功"));
    }

    /**
     * 更新用户状态
     */
    @PutMapping("/users/{id}/status")
    public ResponseEntity<Map<String, Object>> updateUserStatus(
            @PathVariable Long id,
            @RequestBody Map<String, String> request) {
        Optional<User> userOpt = userRepository.findById(id);
        if (userOpt.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("success", false, "message", "用户不存在"));
        }

        User user = userOpt.get();
        String status = request.get("status");
        if (status != null && (status.equals("active") || status.equals("disabled"))) {
            user.setStatus(status);
            userRepository.save(user);
            return ResponseEntity.ok(Map.of("success", true, "message", "状态更新成功"));
        }

        return ResponseEntity.badRequest().body(Map.of("success", false, "message", "无效的状态值"));
    }

    /**
     * 删除用户
     */
    @DeleteMapping("/users/{id}")
    public ResponseEntity<Map<String, Object>> deleteUser(@PathVariable Long id) {
        Optional<User> userOpt = userRepository.findById(id);
        if (userOpt.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("success", false, "message", "用户不存在"));
        }

        userRepository.deleteById(id);
        return ResponseEntity.ok(Map.of("success", true, "message", "删除成功"));
    }
}
