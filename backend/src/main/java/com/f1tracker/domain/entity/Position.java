package com.f1tracker.domain.entity;

// -Represents a single positional update of a driver during an F1 session.public class
// -This is a high frequency entity used for:
//     -Live track visualization
//     -Replay playback
//     -Driver movement analysis

// - Each record corresponds to one driver at one point in time

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "positions", indexes = {
        @Index(name = "idx_position_session_driver", columnList = "session_id, driver_number"),
        @Index(name = "idx_position_timestamp", columnList = "session_id, timestamp")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder 
public class Position {
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
    
    private Integer position;

    private Double x;
    private Double y;
    private Double z;

    @Column(name = "normalized_x")
    private Double normalizedX;

    @Column(name = "normalized_y")
    private Double normalizedY;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist 
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
