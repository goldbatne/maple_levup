const { searchAvatarItems } = require("../../.agents/skills/msw-search/scripts/msw_resource_api.cjs");

const queries = [
  "straw hat", "wooden sword", "peach earrings", "blue flower robe", "panda glove",
  "harp earrings", "red feather cape", "blue dragon glove", "dark dragon cape", "dragon weapon",
  "memory hood", "memory robe", "guardian armor", "guardian shield", "time weapon",
  "space helmet", "space suit", "laser gun", "alien glasses", "ufo accessory",
];

async function main() {
  const output = [];
  for (let i = 0; i < queries.length; i += 4) {
    output.push(...await Promise.all(queries.slice(i, i + 4).map(async (query) => {
      try {
        const response = await searchAvatarItems(query, { topK: 4 });
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
