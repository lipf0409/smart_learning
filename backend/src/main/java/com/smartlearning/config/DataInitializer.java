package com.smartlearning.config;

import com.smartlearning.entity.User;
import com.smartlearning.repository.UserRepository;
import com.smartlearning.service.PasswordService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/**
 * 数据初始化器
 * 在应用启动时自动创建管理员账户
 */
@Component
public class DataInitializer implements CommandLineRunner {

    private static final Logger logger = LoggerFactory.getLogger(DataInitializer.class);

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordService passwordService;

    @Override
    public void run(String... args) throws Exception {
        initAdminUser();
    }

    /**
     * 初始化管理员用户
     */
    private void initAdminUser() {
        // 检查管理员是否已存在
        if (!userRepository.existsByUsername("ll")) {
            User admin = new User();
            admin.setUsername("ll");
            admin.setPassword(passwordService.encode("040920Lp.."));
            admin.setEmail("admin@smartlearning.com");
            admin.setRole("admin");
            admin.setStatus("active");

            userRepository.save(admin);
            logger.info("管理员账户 'll' 创建成功");
        } else {
            logger.info("管理员账户 'll' 已存在");
        }

        // 确保 admin 账户也存在
        if (!userRepository.existsByUsername("admin")) {
            User admin = new User();
            admin.setUsername("admin");
            admin.setPassword(passwordService.encode("admin123"));
            admin.setEmail("admin2@smartlearning.com");
            admin.setRole("admin");
            admin.setStatus("active");

            userRepository.save(admin);
            logger.info("管理员账户 'admin' 创建成功");
        }
    }
}
