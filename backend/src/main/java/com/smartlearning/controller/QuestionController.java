package com.smartlearning.controller;

import com.smartlearning.service.AiService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

@RestController
@RequestMapping("/api/question")
public class QuestionController {

    @Autowired
    private AiService aiService;

    @PostMapping("/solve")
    public ResponseEntity<Map<String, Object>> solveQuestion(
            @RequestParam("file") MultipartFile file) throws IOException {

        Map<String, Object> result = aiService.solveQuestion(file);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        return ResponseEntity.ok(Map.of(
            "status", "ok",
            "claude_api_configured", false
        ));
    }
}