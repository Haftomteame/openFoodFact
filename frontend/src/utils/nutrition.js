const NUTRI_RANK = { A: 1, B: 2, C: 3, D: 4, E: 5 };

export function nutriRank(score) {
  return NUTRI_RANK[String(score || "E").toUpperCase()] || 5;
}

export function nutriImprovement(before, after) {
  return Math.max(0, nutriRank(before) - nutriRank(after));
}

export function computeSubstitutionStats(substitutions) {
  const total = substitutions.length;
  let improved = 0;
  let totalSteps = 0;

  for (const sub of substitutions) {
    const before = sub.original_nutri_score;
    const after = sub.substitute_nutri_score;
    if (before && after) {
      const steps = nutriImprovement(before, after);
      if (steps > 0) {
        improved += 1;
        totalSteps += steps;
      }
    }
  }

  return {
    total,
    improved,
    averageSteps: improved ? (totalSteps / improved).toFixed(1) : "0",
  };
}
