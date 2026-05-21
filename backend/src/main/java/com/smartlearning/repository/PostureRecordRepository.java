package com.smartlearning.repository;

import com.smartlearning.entity.PostureRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PostureRecordRepository extends JpaRepository<PostureRecord, Long> {

    List<PostureRecord> findByUserIdOrderByDetectedAtDesc(Long userId);
}