import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const skill = await readFile(new URL('../skills/connect-saas.md', import.meta.url), 'utf8');
const githubSection = skill.match(/## GitHub remote MCP\n([\s\S]*?)\n## Examples/)?.[1];

test('documents the GitHub PAT path instead of unsupported DCR', () => {
  assert.ok(githubSection, 'GitHub remote MCP section should exist');
  assert.match(githubSection, /does not support Dynamic Client Registration/);
  assert.match(
    githubSection,
    /Do not send the user through \*\*Start OAuth Flow\*\* without a configured/
  );
  assert.match(githubSection, /agor_widgets_request_env_vars/);
  assert.match(githubSection, /GITHUB_MCP_PAT/);
  assert.match(githubSection, /instead of creating a duplicate/);
});

test('keeps the provider links and least-privilege variants discoverable', () => {
  assert.match(
    githubSection,
    /https:\/\/github\.com\/settings\/personal-access-tokens\/new/
  );
  assert.match(githubSection, /https:\/\/api\.githubcopilot\.com\/mcp\/readonly/);
  assert.match(githubSection, /contents=read&issues=read&pull_requests=read/);
  assert.match(githubSection, /Only select repositories/);
});

test('keeps widget and MCP examples valid JSON with a templated bearer token', () => {
  const jsonBlocks = [...githubSection.matchAll(/\s*```json\n([\s\S]*?)\n\s*```/g)].map(
    (match) => JSON.parse(match[1].replace(/^ {3}/gm, ''))
  );

  assert.equal(jsonBlocks.length, 2);
  assert.deepEqual(jsonBlocks[0].names, ['GITHUB_MCP_PAT']);
  assert.equal(jsonBlocks[0].variable_metadata.GITHUB_MCP_PAT.input_type, 'password');
  assert.equal(jsonBlocks[1].auth.type, 'bearer');
  assert.equal(jsonBlocks[1].auth.token, '{{ user.env.GITHUB_MCP_PAT }}');
});
