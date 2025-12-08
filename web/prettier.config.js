/** @type {import('prettier').Config & import('prettier-plugin-tailwindcss').PluginOptions} */
const config = {
  semi: false, // 社区推荐不使用分号
  singleQuote: true, // 社区推荐使用单引号
  trailingComma: 'all', // 社区推荐使用尾逗号
  printWidth: 120, // 社区推荐使用120字符
  //  prettier-plugin-tailwindcss
  plugins: ['prettier-plugin-tailwindcss', '@trivago/prettier-plugin-sort-imports', 'prettier-plugin-organize-imports'],
  tabWidth: 2, // 社区推荐使用2个空格
  proseWrap: 'never', // 社区推荐不自动换行
  endOfLine: 'lf', // 社区推荐使用LF

  jsxSingleQuote: true, // 社区推荐使用单引号
  jsxBracketSameLine: false, // 社区推荐不将JSX的 > 放在最后一行
  arrowParens: 'always', // 社区推荐总是使用箭头函数的参数括号
  bracketSpacing: true,
  tailwindStylesheet: 'src/index.css', // v4 需要指定 Tailwind CSS 样式入口
  importOrder: ['^@core/(.*)$', '^@server/(.*)$', '^@ui/(.*)$', '^[./]'],
  importOrderSeparation: true,
  importOrderSortSpecifiers: true,
  overrides: [
    {
      files: '.prettierrc',
      options: {
        parser: 'json',
      },
    },
    {
      files: 'document.ejs',
      options: {
        parser: 'html',
      },
    },
  ],
}

export default config
