// render_math.js: stdin {mode, tex} -> stdout MathJax SVG
const { mathjax } = require('mathjax-full/js/mathjax.js');
const { TeX } = require('mathjax-full/js/input/tex.js');
const { SVG } = require('mathjax-full/js/output/svg.js');
const { liteAdaptor } = require('mathjax-full/js/adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = require('mathjax-full/js/handlers/html.js');
// 显式加载常用宏包配置
require('mathjax-full/js/input/tex/base/BaseConfiguration.js');
require('mathjax-full/js/input/tex/ams/AmsConfiguration.js');
require('mathjax-full/js/input/tex/noundefined/NoUndefinedConfiguration.js');
require('mathjax-full/js/input/tex/boldsymbol/BoldsymbolConfiguration.js');
require('mathjax-full/js/input/tex/newcommand/NewcommandConfiguration.js');
require('mathjax-full/js/input/tex/configmacros/ConfigMacrosConfiguration.js');
require('mathjax-full/js/input/tex/action/ActionConfiguration.js');
require('mathjax-full/js/input/tex/require/RequireConfiguration.js');
require('mathjax-full/js/input/tex/color/ColorConfiguration.js');
require('mathjax-full/js/input/tex/textmacros/TextMacrosConfiguration.js');
require('mathjax-full/js/input/tex/mathtools/MathtoolsConfiguration.js');
require('mathjax-full/js/input/tex/cases/CasesConfiguration.js');
require('mathjax-full/js/input/tex/textcomp/TextcompConfiguration.js');
require('mathjax-full/js/input/tex/centernot/CenternotConfiguration.js');
require('mathjax-full/js/input/tex/empheq/EmpheqConfiguration.js');
require('mathjax-full/js/input/tex/colortbl/ColortblConfiguration.js');

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const tex = new TeX({
  packages: ['base', 'ams', 'noundefined', 'boldsymbol', 'newcommand',
             'configmacros', 'action', 'require', 'color', 'textmacros',
             'mathtools', 'cases', 'textcomp', 'centernot'],
  macros: {
    rmone: ['\\mathrm{one}'], rmtwo: ['\\mathrm{two}'],
    GbLI: ['\\mathrm{GbLI}'], SbLI: ['\\mathrm{SbLI}'], PTA: ['\\mathrm{PTA}'],
    uhat: ['\\hat{u}'], vhat: ['\\hat{v}'], shat: ['\\hat{s}'], nhat: ['\\hat{n}'],
    thetahat: ['\\hat{\\theta}'], phihat: ['\\hat{\\phi}'],
    dhat: ['\\hat{d}'],
  }
});
const svg = new SVG({ fontCache: 'local', ex: 8, containerWidth: 800 });
const doc = mathjax.document('', { InputJax: tex, OutputJax: svg });

const chunks = [];
process.stdin.on('data', d => chunks.push(d));
process.stdin.on('end', () => {
  const { mode, tex: t } = JSON.parse(Buffer.concat(chunks).toString('utf8'));
  const node = doc.convert(t, { display: mode === 'display' });
  const out = adaptor.outerHTML(node);
  const m = out.match(/<svg[\s\S]*?<\/svg>/);
  process.stdout.write(m ? m[0] : out);
});
