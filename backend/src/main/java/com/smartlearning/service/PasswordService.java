package com.smartlearning.service;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * 密码加密服务
 * 使用 bcrypt 算法进行密码哈希加密
 * 应用级盐值 "556920ly" 提供额外安全层
 */
@Service
public class PasswordService {

    /**
     * 应用级盐值，在 bcrypt 加密前与密码组合
     */
    private static final String APP_SALT = "556920ly";

    /**
     * BCrypt 编码器，工作因子设为 12（推荐值）
     * 工作因子越高，计算越复杂，安全性越高，但耗时也越长
     */
    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);

    /**
     * 加密密码
     * @param rawPassword 原始密码
     * @return 加密后的哈希值
     */
    public String encode(String rawPassword) {
        if (rawPassword == null || rawPassword.isEmpty()) {
            throw new IllegalArgumentException("密码不能为空");
        }
        // 将应用级盐值与密码组合后再进行 bcrypt 加密
        String saltedPassword = rawPassword + APP_SALT;
        return encoder.encode(saltedPassword);
    }

    /**
     * 验证密码是否匹配
     * @param rawPassword 原始密码
     * @param encodedPassword 加密后的哈希值
     * @return 是否匹配
     */
    public boolean matches(String rawPassword, String encodedPassword) {
        if (rawPassword == null || rawPassword.isEmpty()) {
            return false;
        }
        if (encodedPassword == null || encodedPassword.isEmpty()) {
            return false;
        }
        // 将应用级盐值与密码组合后再进行验证
        String saltedPassword = rawPassword + APP_SALT;
        return encoder.matches(saltedPassword, encodedPassword);
    }
}
