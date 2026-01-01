package com.f1tracker.domain.entity;

// This class maps to the "drivers" table in the database
// It stores master data for F1 drivers and is managed via JPA/Hibernate

// Purpose:
// - Maps a database row to a java object
// - Used by repositories, services, and controllers
// - Automatically handles timestamps on create / update

import jakarta.persistence.*;
import lombok.*;

import java.lang.annotation.Inherited;
import java.time.LocalDateTime;

@Entity
@Table(name = "drivers")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Driver {
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "driver_number", unique = true, nullable = false)
    private Integer driverNumber;

    @Column(nullable = false)
    private String name;

    private String team;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
