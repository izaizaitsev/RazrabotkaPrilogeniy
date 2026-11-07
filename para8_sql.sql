-- Пара 8 — SQL выборки по StPlatform


-- (a) Все сдачи студента по фамилии.

SELECT  u.full_name,
		    s.assignment_id,
        s.link,
        s.status
FROM submissions s
JOIN users u      ON u.id = s.student_id
JOIN assignment a ON a.id = s.assignment_id
WHERE u.full_name LIKE 'Иванов %'


-- (b) Сколько сдач пришло на каждое задание.

SELECT a.pair_number,
       a.title,
       COUNT(s.id)
FROM assignment a
LEFT JOIN submissions s ON s.assignment_id = a.id
GROUP BY a.id, a.pair_number, a.title


-- (c) Cтуденты, не сдавшие ни одной работы.

SELECT u.full_name,
       u.telegram,
       u.email
FROM users u
LEFT JOIN submissions s ON s.student_id = u.id
WHERE u.role = 'STUDENT'
AND s.id IS NULL