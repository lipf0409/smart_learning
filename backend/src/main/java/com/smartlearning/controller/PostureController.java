package com.smartlearning.controller;

import com.smartlearning.service.AiService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

@RestController
@RequestMapping("/api/posture")
public class PostureController {

    @Autowired
    private AiService aiService;

    @PostMapping("/detect")
    public ResponseEntity<Map<String, Object>> detectPosture(
            @RequestParam("file") MultipartFile file) throws IOException {

        Map<String, Object> result = aiService.detectPosture(file);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "ok"));
    }
}