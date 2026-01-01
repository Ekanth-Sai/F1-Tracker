package com.f1tracker.domain.entity;

// - This class represents an F1 session (Race, Quali, Practice) and maps directly to the "sessions" table in the database

// Purpose:
// - Acts as the root entity for all session - related data
// - Referenced by positions, telemetry, pit stops, and stats 
// - Used to track live vs completed sessions


import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
@Entity
@Table(name = "sessions")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder 
public class Session {
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "session_key", unique = true, nullable = false)
    private String sessionKey;

    @Column(name = "session_name", nullable = false)
    private String sessionName;

    @Column(name = "session_type")
    private String sessionType;

    @Column(name = "circuit_name")
    private String circuitName;

    private String country;

    @Column(name = "start_time", nullable = false)
    private LocalDateTime startTime;

    @Column(name="end_time")
    private LocalDateTime endTime;

    @Column(name = "is_live")
    private Boolean isLive;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        
        if (isLive == null) {
            isLive = false;
        }
    }

}
