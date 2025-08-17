import { randomUUIDv7 } from "bun";
import { Hono } from "hono";
import { validator } from "hono/validator";
import z from "zod";
import { collection } from "../lib";
import { serveStatic } from "hono/bun";

const AddSchema = z.object({
  files: z.array(
    z.instanceof(File).refine(
      (f) =>
        ["application/octet-stream", "model/fbx"].includes(f.type) ||
        f.name.toLowerCase().endsWith(".fbx") || {
          message: "Only .fbx files are allowed",
        }
    )
  ),
  label: z.string(),
});

const SearchSchema = z.object({
  query: z.string(),
});

const app = new Hono();

app.post(
  "/add",
  validator("form", (value, c) => {
    const parsed = AddSchema.safeParse(value);
    if (!parsed.success) {
      return c.text("Invalid Body.", 401);
    }
    return parsed.data;
  }),
  async (c) => {
    try {
      const body = c.req.valid("form");

      await Promise.all(
        body.files.map(async (file) => {
          const id = randomUUIDv7();
          const arrayBuffer = await file.arrayBuffer();
          const buf = Buffer.from(arrayBuffer);
          let extension = "";
          if (file.name.toLowerCase().endsWith(".fbx")) {
            extension = "fbx";
          } else {
            throw new Error("不正な拡張子です。");
          }
          const path = `motion/${id}.${extension}`;
          await Bun.write(path, buf);
          collection.add({ ids: [id], documents: [body.label] });
        })
      );

      return c.json({
        error: "モーションが正常に追加されました。",
      });
    } catch (e) {
      return c.json({
        error: "ファイルをアップロード中にエラーが発生しました。",
      });
    }
  }
);

app.post(
  "/search",
  validator("query", (value, c) => {
    const parsed = SearchSchema.safeParse(value);
    if (!parsed.success) {
      return c.text("Invalid Query.", 401);
    }
    return parsed.data;
  }),
  async (c) => {
    try {
      const body = c.req.valid("query");

      const res = await collection.query({ queryTexts: [body.query] });

      if (res.ids.length <= 0 || !res.ids[0]) {
        return c.json({
          error: "モーションが見つかりませんでした。",
        });
      } else {
        return c.json({
          id: res.ids[0],
        });
      }
    } catch (e) {
      return c.json({
        error: "検索中にエラーが発生しました。",
      });
    }
  }
);

app.use("/motions/*", serveStatic({ root: "./" }));

export default app;
