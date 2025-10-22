INSERT INTO dbo.tbl_pomodoro_rules(difficulty_level, focus_duration, break_duration, description, created_date) 
VALUES
    ('Paso de bebe', 10, 5, 'Ideal para principiantes que están comenzando a desarrollar su capacidad de concentración.', GETDATE()),
    ('Popular', 25, 5, 'El método Pomodoro clásico que equilibra períodos de trabajo y descanso para maximizar la productividad.', GETDATE()),
    ('Medio', 40, 8, 'Para usuarios con experiencia que buscan sesiones de trabajo más largas y descansos adecuados.', GETDATE()),
    ('Intenso', 60, 10, 'Diseñado para usuarios avanzados que desean maximizar su tiempo de concentración con períodos de trabajo prolongados.', GETDATE()),
    ('Extendido', 80, 13, 'Para usuarios expertos que buscan sesiones de trabajo extendidas con descansos más largos para mantener la productividad.', GETDATE());