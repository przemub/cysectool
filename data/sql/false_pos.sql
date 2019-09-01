DROP VIEW IF EXISTS false_pos;
CREATE VIEW false_pos
AS
	SELECT results.tool, results.category, Sum(pass) AS true_neg, Count(pass)-Sum(pass) AS false_pos, 1-Round(Sum(pass)*1.0/(Count(pass)),3) AS score
	FROM results
	WHERE (((results.real)=0))
	GROUP BY results.tool, results.category;
;

DROP VIEW IF EXISTS true_pos;
CREATE VIEW true_pos
AS
	SELECT results.tool, results.category, Sum(pass) AS true_pos, Count(pass)-Sum(pass) AS false_neg, Round(Sum(pass)*1.0/(Count(pass)),3) AS score
	FROM results
	WHERE (((results.real)=1))
	GROUP BY results.tool, results.category
;

DROP VIEW IF EXISTS score;
CREATE VIEW score
AS
	SELECT true_pos.tool, true_pos.category, true_pos.score AS true_pos_score, false_pos.score AS false_pos_score, Round([true_pos].[score]-[false_pos].[score],3) AS youden
	FROM true_pos INNER JOIN false_pos ON (true_pos.category = false_pos.category) AND (true_pos.tool = false_pos.tool);
;

DROP VIEW IF EXISTS score_by_tool;
CREATE VIEW score_by_tool
AS
	SELECT score.tool, Round(Avg(score.true_pos_score),3) AS true_pos_score, Round(Avg(score.false_pos_score),3) AS false_pos_score, Round(Avg(score.youden),3) AS youden,
		ROUND((true_pos_score+false_pos_score)*100) AS cost
	FROM score
	GROUP BY score.tool
;

