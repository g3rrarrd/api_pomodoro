-- =====================================================
-- TABLA: tbl_users
-- =====================================================
CREATE TABLE tbl_users (
    id_user INT IDENTITY(1,1) PRIMARY KEY,
    nickname VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_date DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET()
);

-- =====================================================
-- TABLA: tbl_sessions
-- =====================================================
CREATE TABLE tbl_sessions (
    id_session INT IDENTITY(1,1) PRIMARY KEY,
    id_user INT NOT NULL,
    session_name VARCHAR(100) NOT NULL,
    total_focus_seconds INT DEFAULT 0,
    total_break_seconds INT DEFAULT 0,
    total_pause_seconds INT DEFAULT 0,
    created_date DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
    CONSTRAINT fk_sessions_user FOREIGN KEY (id_user)
        REFERENCES tbl_users(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================
-- TABLA: tbl_pomodoro_rules
-- =====================================================
CREATE TABLE tbl_pomodoro_rules (
    id_pomodoro_rule INT IDENTITY(1,1) PRIMARY KEY,
    difficulty_level VARCHAR(50) NOT NULL UNIQUE,
    focus_duration INT NOT NULL,
    break_duration INT NOT NULL,
    description TEXT NULL,
    created_date DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET()
);

-- =====================================================
-- TABLA: tbl_pomodoro_types
-- =====================================================
CREATE TABLE tbl_pomodoro_types (
    id_pomodoro_type INT IDENTITY(1,1) PRIMARY KEY,
    name_type VARCHAR(50) NOT NULL UNIQUE
);

-- =====================================================
-- TABLA: tbl_pomodoro_details
-- =====================================================
CREATE TABLE tbl_pomodoro_details (
    id_pomodoro_detail INT IDENTITY(1,1) PRIMARY KEY,
    id_session INT NOT NULL,
    id_pomodoro_rule INT NOT NULL,
    id_pomodoro_type INT NOT NULL,
    event_type VARCHAR(20) NOT NULL,
    planned_duration INT NOT NULL,
    is_completed BIT DEFAULT 0,
    focus_time INT DEFAULT 0,
    break_time INT DEFAULT 0,
    notes TEXT NULL,
    created_date DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
    CONSTRAINT fk_pomodoro_session FOREIGN KEY (id_session)
        REFERENCES tbl_sessions(id_session)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_pomodoro_rule FOREIGN KEY (id_pomodoro_rule)
        REFERENCES tbl_pomodoro_rules(id_pomodoro_rule)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_pomodoro_type FOREIGN KEY (id_pomodoro_type)
        REFERENCES tbl_pomodoro_types(id_pomodoro_type)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT ck_pomodoro_event_type CHECK (event_type IN ('focus', 'break'))
);

-- =====================================================
-- TABLA: tbl_pause_tracking
-- =====================================================
CREATE TABLE tbl_pause_tracking (
    id_pause INT IDENTITY(1,1) PRIMARY KEY,
    id_pomodoro_detail INT NOT NULL,
    pause_start DATETIMEOFFSET NOT NULL,
    pause_end DATETIMEOFFSET NULL,
    total_pause_seconds INT DEFAULT 0,
    created_date DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
    CONSTRAINT fk_pause_pomodoro FOREIGN KEY (id_pomodoro_detail)
        REFERENCES tbl_pomodoro_details(id_pomodoro_detail)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ==========================================================
-- sesiones por usuario
-- ==========================================================
CREATE INDEX indx_sesion_user ON tbl_sessions (id_user)

-- ==========================================================
-- Pomodoros por sesion
-- ==========================================================
CREATE INDEX indx_bit_pomodoro 
ON tbl_pomodoro_details (
    id_session
    )
INCLUDE (focus_time, break_time, is_completed)


-- ==========================================================
-- Pausas por pomodoro
-- ==========================================================
CREATE INDEX indx_bit_pause 
ON tbl_pause_tracking (
    id_pomodoro_detail, 
    pause_start
    )