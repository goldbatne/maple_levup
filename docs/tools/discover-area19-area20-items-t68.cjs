const { searchAvatarItems } = require("../../.agents/skills/msw-search/scripts/msw_resource_api.cjs");

const queries = [
  "Cygnus knight helmet", "Cygnus knight cape", "Empress glove", "Empress shoes", "Empress weapon",
  "dark stump hat", "iron boar armor", "stone mask", "golem glove", "tree weapon",
  "Cygnus dress", "royal guard sword", "royal guard boots", "twilight sword",
  "stone hammer", "dark golem weapon", "stumpy axe", "ancient weapon",
];

async function main() {
  const output = [];
  for (let i = 0; i < queries.length; i += 4) {
    output.push(...await Promise.all(queries.slice(i, i + 4).map(async (query) => {
      try {
        const response = await searchAvatarItems(query, { topK: 6 });
        return {
          query,
          results: (response.results || []).map((entry) => ({
            id: entry.id,
            names: entry.names,
            score: entry.score,
            category: entry.category,
            subCategory: entry.sub_category,
            slot: entry.slot,
          })),
        };
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
