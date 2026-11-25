# How open-diagram compares

The same photo upload flow, drawn by each tool from its own format with default settings.

## open-diagram

![The photo upload flow drawn by open-diagram](images/compare/open-diagram.png)

Made in 0.59 s. 0 layout problems. [Source](https://github.com/lukendeasy/open-diagram/blob/main/docs/compare/photo-upload.json)

## Mermaid

![The photo upload flow drawn by Mermaid](images/compare/mermaid.png)

Made in 0.76 s. [Source](https://github.com/lukendeasy/open-diagram/blob/main/docs/compare/photo-upload.mmd)

## D2

![The photo upload flow drawn by D2](images/compare/d2.png)

Made in 0.017 s. [Source](https://github.com/lukendeasy/open-diagram/blob/main/docs/compare/photo-upload.d2)

## Excalidraw

![The photo upload flow drawn by Excalidraw](images/compare/excalidraw.png)

Made in 0.020 s inside the browser, from the Mermaid file. [Source](https://github.com/lukendeasy/open-diagram/blob/main/docs/compare/photo-upload.mmd)

## archify

![The photo upload flow drawn by archify](images/compare/archify.png)

Made in 0.28 s. Its layout checks passed. [Source](https://github.com/lukendeasy/open-diagram/blob/main/docs/compare/photo-upload.architecture.json)

## Only open-diagram and archify check every layout

| Tool | Input | Layout | Checks layout | Output | MCP | License | Price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [open-diagram](https://github.com/lukendeasy/open-diagram) | Python, JSON, Mermaid | Automatic | Yes | SVG, PNG | Yes | MIT | Free |
| [Mermaid](https://mermaid.js.org) | Text | Automatic | No | SVG, PNG, PDF | Yes | MIT | Free; paid app from $10 a user a month, billed yearly |
| [D2](https://d2lang.com) | Text | Automatic | No | SVG, PNG, PDF, PowerPoint, GIF, ASCII | No | MPL-2.0 | Free; its TALA layout engine needs a license for commercial use |
| [draw.io](https://www.drawio.com) | Editor | By hand | Only in its MCP viewer | PNG, SVG, PDF and more | Yes | Apache-2.0 | Free |
| [Excalidraw](https://excalidraw.com) | Editor | By hand | Only in its paid MCP server | PNG, SVG | Yes | MIT | Free; Plus from $6 a user a month |
| [archify](https://github.com/tt-a1i/archify) | JSON | Placed in the file, or automatic when chosen | Yes | Interactive HTML page; PNG, WebP or JPG; PDF by printing | No | Apache-2.0 | Free |

MCP lets AI apps such as Claude and Cursor use a tool directly. Each tool drew the same boxes and bullets. Times run from source file to finished SVG on one Mac; each is the median of five runs.
