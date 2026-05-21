package com.smartlearning.repository;

import com.smartlearning.entity.QuestionRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface QuestionRecordRepository extends JpaRepository<QuestionRecord, Long> {

    List<QuestionRecord> findByUserIdOrderByCreatedAtDesc(Long userId);
}