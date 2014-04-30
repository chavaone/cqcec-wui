(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['ipinfo'] = template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression;


  buffer += "<div>\n	<header id=\"ip_info_header\" class=\"page_header\">\n		<button type=\"button\" class=\"btn btn-default icon-chevron-left\" onclick=\"app.populate_map_area()\"></button>\n		<h3>";
  if (stack1 = helpers.ip) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = (depth0 && depth0.ip); stack1 = typeof stack1 === functionType ? stack1.call(depth0, {hash:{},data:data}) : stack1; }
  buffer += escapeExpression(stack1)
    + "</h3>\n	</header>\n	<ul class=\"nav nav-pills\">\n		<li id=\"outgoing_tab\">\n			<a href=\"javascript:void(0)\" onclick=\"app.enable_ip_info_tab('";
  if (stack1 = helpers.ip) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = (depth0 && depth0.ip); stack1 = typeof stack1 === functionType ? stack1.call(depth0, {hash:{},data:data}) : stack1; }
  buffer += escapeExpression(stack1)
    + "', 'Outgoing')\">\n				<span class=\"glyphicon glyphicon-chevron-up pull-left\"></span>Saíntes<span class=\"badge pull-right\">";
  if (stack1 = helpers.outgoing_conn) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = (depth0 && depth0.outgoing_conn); stack1 = typeof stack1 === functionType ? stack1.call(depth0, {hash:{},data:data}) : stack1; }
  buffer += escapeExpression(stack1)
    + "</span>\n			</a>\n		</li>\n		<li id=\"incoming_tab\">\n			<a href=\"javascript:void(0)\" onclick=\"app.enable_ip_info_tab('";
  if (stack1 = helpers.ip) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = (depth0 && depth0.ip); stack1 = typeof stack1 === functionType ? stack1.call(depth0, {hash:{},data:data}) : stack1; }
  buffer += escapeExpression(stack1)
    + "', 'Incoming')\">\n				<span class=\"glyphicon glyphicon-chevron-down pull-left\"></span>Entrantes<span class=\"badge pull-right\">";
  if (stack1 = helpers.incoming_conn) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = (depth0 && depth0.incoming_conn); stack1 = typeof stack1 === functionType ? stack1.call(depth0, {hash:{},data:data}) : stack1; }
  buffer += escapeExpression(stack1)
    + "</span>\n			</a>\n		</li>\n\n		<li id=\"stats_tab\" class=\"disabled\">\n			<a href=\"javascript:void(0)\" onclick=\"app.enable_ip_stats('";
  if (stack1 = helpers.ip) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = (depth0 && depth0.ip); stack1 = typeof stack1 === functionType ? stack1.call(depth0, {hash:{},data:data}) : stack1; }
  buffer += escapeExpression(stack1)
    + "')\" >\n				<span class=\"glyphicon glyphicon-stats\"></span>\n				Estatísticas\n			</a>\n		</li>\n	</ul>\n	<div id=\"ip_info_body\">\n	</div>\n</div>";
  return buffer;
  });
})();