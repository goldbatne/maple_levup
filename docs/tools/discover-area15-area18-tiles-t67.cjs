const { searchResources, getResource } = require("../../.agents/skills/msw-search/scripts/msw_resource_api.cjs");

const queries = [
  "Mu Lung peach blossom stone path", "Mu Lung dojo bamboo floor",
  "Minar Forest dragon nest grass stone", "Leafre dragon forest ground",
  "Temple of Time marble floor clock stone", "Memory Lane temple floor",
  "Omega Sector metal floor sci fi", "Earth Defense HQ alien base floor",
];

const selected = [
  ["Mu Lung", "975ef012af6e4d29a252dda48606d3dc"], ["Mu Lung", "9b5ff173add14b06bc3aaed743bc9d7d"],
  ["Mu Lung", "9b2c01ea1bc84dd0bf181131442657a6"], ["Mu Lung", "6688a017ab6b40f8a1408a65a11cb0de"],
  ["Minar Forest", "f814de595d964e5abb032d2bead4bf66"], ["Minar Forest", "748ed7c7563646f2aba54579a4dc95a4"],
  ["Minar Forest", "3fcc80179fcb46c1a449311535665743"], ["Minar Forest", "3f2600f7423c481093224c0ef1a5521f"],
  ["Temple of Time", "e29340ee40e3456baada5c3b8c3910ea"], ["Temple of Time", "a6dc5b775a5047e0b61d9b36805c4e84"],
  ["Temple of Time", "424069dae68a4f00affc331809d42777"], ["Temple of Time", "bb78629e1a994dc4a8f66b9468e44fc7"],
  ["Omega Sector", "58516c958f66438aae297e1ee3c7e8a8"], ["Omega Sector", "7fb4801b267f47a89240399f42b04d76"],
  ["Omega Sector", "5361eaba4aa94edea80960447ac2205f"], ["Omega Sector", "c2f14d9e49fd404bb3827b4cd0738088"],
];

async function main() {
  if (process.argv[2] === "selected") {
    const output = [];
    for (let i = 0; i < selected.length; i += 4) {
      output.push(...await Promise.all(selected.slice(i, i + 4).map(async ([area, id]) => {
        const resource = await getResource(id);
        return { area, id, type:resource.type, category:resource.category, dname:resource.dname,
          width:resource.payload?.width, height:resource.payload?.height, thumbnail:resource.payload?.thumbnail };
      })));
    }
    console.log(JSON.stringify(output, null, 2));
    return;
  }
  if (process.argv[2] === "detail" && process.argv[3]) {
    console.log(JSON.stringify(await getResource(process.argv[3]), null, 2));
    return;
  }
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
