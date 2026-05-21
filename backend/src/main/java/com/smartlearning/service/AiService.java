package com.smartlearning.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

/**
 * Service for calling AI Service endpoints
 */
@Service
public class AiService {

    @Value("${ai.service.url}")
    private String aiServiceUrl;

    /**
     * Call posture detection API
     */
    public Map<String, Object> detectPosture(MultipartFile file) throws IOException {
        // For now, return mock response
        // In production, this would call the actual AI service via WebClient or RestTemplate
        return Map.of(
            "status", "good",
            "confidence", 0.85,
            "message", "坐姿良好，请保持"
        );
    }

    /**
     * Call question solving API
     */
    public Map<String, Object> solveQuestion(MultipartFile file) throws IOException {
        // For now, return mock response
        return Map.of(
            "question_text", "[示例题目]",
            "answer", "示例答案",
            "steps", java.util.List.of("步骤1", "步骤2"),
            "knowledge_points", java.util.List.of("知识点1"),
            "success", true
        );
    }
}