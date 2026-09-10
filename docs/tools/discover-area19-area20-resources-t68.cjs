const { searchResources, getResource } = require("../../.agents/skills/msw-search/scripts/msw_resource_api.cjs");

const candidates = [
  ["Future Door", "Official Knight C"],
  ["Future Door", "Official Knight D"],
  ["Future Door", "Advanced Knight A"],
  ["Future Door", "Advanced Knight B"],
  ["Future Door", "Cygnus"],
  ["Twilight Perion", "Mutant Dark Stump"],
  ["Twilight Perion", "Mutant Iron Boar"],
  ["Twilight Perion", "Mutant Stone Mask"],
  ["Twilight Perion", "Ancient Dark Golem"],
  ["Twilight Perion", "Mutant Stumpy"],
];

async function searchOne([area, query]) {
  try {
    const response = await searchResources(query, {
      resourceTypeFilter: ["resource_pack"],
      categoryFilter: ["mob"],
      topK: 5,
    });
    return {
      area,
      query,
      results: (response.results || []).map((entry) => ({
        id: entry.id,
        names: entry.names,
        score: entry.score,
      })),
    };
  } catch (error) {
    return { area, query, error: String(error) };
  }
}

async function main() {
  if (process.argv[2] === "details") {
    const ids = process.argv.slice(3);
    const output = [];
    for (let i = 0; i < ids.length; i += 4) {
      output.push(...await Promise.all(ids.slice(i, i + 4).map(async (id) => {
        try {
          const pack = await getResource(id);
          return {
            id,
            names: pack.names,
            elements: (pack.payload?.elements || [])
              .filter((entry) => /(^|\/)(stand|move|jump|fly|attack\d*|skill\d*|hit\d*|die\d*|ball|effect\d*|areaWarning)(\/|$)/i.test(entry.rel_path || ""))
              .map((entry) => ({ path: entry.rel_path, type: entry.resource_type, ruid: entry.ruid })),
          };
        } catch (error) {
          return { id, error: String(error) };
        }
      })));
    }
    console.log(JSON.stringify(output, null, 2));
    return;
  }
  const output = [];
  for (let i = 0; i < candidates.length; i += 4) {
    output.push(...await Promise.all(candidates.slice(i, i + 4).map(searchOne)));
  }
  console.log(JSON.stringify(output, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
