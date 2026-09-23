const vlSpec_c2 = {
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
};

vegaEmbed('#svg-c2', vlSpec_c2, { renderer: 'svg' }).catch(console.error);

function vega_lite_spec_c2() {
  return vlSpec_c2;
}
function vega_spec_c2() {
  return vegaLite.compile(vega_lite_spec_c2()).spec;
}