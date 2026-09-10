const { searchResources } = require("../../.agents/skills/msw-search/scripts/msw_resource_api.cjs");

const queries = [
  "Future Ereve dark stone floor", "Knight Stronghold purple floor", "Cygnus Garden dark marble", "corrupted Ereve abyss",
  "Twilight Perion red rock ground", "Twilight Perion burnt land", "Twilight Perion excavation stone", "Twilight Perion lava chasm",
];

async function main() {
  const output = [];
  for (let i = 0; i < queries.length; i += 4) {
    output.push(...await Promise.all(queries.slice(i, i + 4).map(async (query) => {
      try {
        const response = await searchResources(query, {
          resourceTypeFilter: ["sprite", "animationclip", "resource_pack"],
          topK: 5,
        });
        return { query, results: (response.results || []).map((entry) => ({
          id: entry.id,
          names: entry.names,
          type: entry.resource_type,
          category: entry.category,
          score: entry.score,
        })) };
      } catch (error) {
        return { query, error: String(error) };
      }
    })));
  }
  console.log(JSON.stringify(output, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
