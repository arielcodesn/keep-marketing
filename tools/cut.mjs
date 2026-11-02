// Usage: node cut.mjs <inDir> <outDir> [model]
// Writes an RGBA PNG (hamster only) for every PNG frame in inDir.
import { removeBackground } from "@imgly/background-removal-node";
import fs from "node:fs";
import path from "node:path";

const [inDir, outDir, model = "medium"] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const files = fs.readdirSync(inDir).filter((f) => f.endsWith(".png")).sort();
const t0 = Date.now();
for (const f of files) {
  const out = path.join(outDir, f);
  if (fs.existsSync(out)) continue;
  const blob = await removeBackground("file://" + path.resolve(inDir, f), {
    model,
    output: { format: "image/png", quality: 1 },
  });
  fs.writeFileSync(out, Buffer.from(await blob.arrayBuffer()));
}
console.log(`${files.length} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
