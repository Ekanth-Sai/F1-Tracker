package com.f1tracker.domain.entity;

// -Represents raw telemetry data collected from a driver during an F1 session.
// -This is a high-frequency, write-heavy entity used for:
//     -Speed and RPM charts
//     -Throttle/brake analysis
//     -ML feature extraction
//     -Replay and performance analysis

// -Each record corresponds to one telemetry snapshot for a driver at a specified moment in time.

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "telemetry", indexes = {
        @Index(name = "idx_telemetry_session_driver", columnList = "session_id, driver_number"),
        @Index(name = "idx_telemetry_timestamp", columnList = "session_id, timestamp")
})
@Data 
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Telemetry {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "session_id", nullable = false)
    private Long sessionId;

    @Column(name = "driver_number", nullable = false)
    private Integer driverNumber;

    @Column(nullable = false)
    private LocalDateTime timestamp;

    @Column(nullable = false)
    private LocalDateTime date;

    private Integer speed;
    private Integer rpm;

    @Column(name = "n_gear")
    private Integer nGear;

    private Integer throttle;
    private Boolean brake;
    private Integer drs;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
