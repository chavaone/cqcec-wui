(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['networkmap'] = template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing, self=this;

function program1(depth0,data) {
  
  var buffer = "", stack1, stack2, options;
  buffer += "\n	<li id=\"conn"
    + escapeExpression(((stack1 = ((stack1 = data),stack1 == null || stack1 === false ? stack1 : stack1.index)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "\" class=\"connected_ip\" onclick=\"app.enable_ip_info('"
    + escapeExpression(((stack1 = ((stack1 = data),stack1 == null || stack1 === false ? stack1 : stack1.key)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "')\">\n		<span class=\"moonicon-screen type_icon\"></span>\n		<ul class=\"ip_info\">\n			<li class=\"ip\">"
    + escapeExpression(((stack1 = ((stack1 = data),stack1 == null || stack1 === false ? stack1 : stack1.key)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "</li>\n			<li class=\"hostname\">";
  if (stack2 = helpers.hostname) { stack2 = stack2.call(depth0, {hash:{},data:data}); }
  else { stack2 = (depth0 && depth0.hostname); stack2 = typeof stack2 === functionType ? stack2.call(depth0, {hash:{},data:data}) : stack2; }
  buffer += escapeExpression(stack2)
    + " </li>\n			<li class=\"macvendor\">";
  if (stack2 = helpers.vendor) { stack2 = stack2.call(depth0, {hash:{},data:data}); }
  else { stack2 = (depth0 && depth0.vendor); stack2 = typeof stack2 === functionType ? stack2.call(depth0, {hash:{},data:data}) : stack2; }
  buffer += escapeExpression(stack2)
    + " </li>\n		</ul>\n		<ul class=\"numconn\">\n			<li>\n				<span class=\"glyphicon glyphicon-chevron-up pull-left\"></span>\n				Saíntes\n				<span class=\"badge pull-right\">";
  options = {hash:{},data:data};
  stack2 = ((stack1 = helpers.connnum || (depth0 && depth0.connnum)),stack1 ? stack1.call(depth0, (depth0 && depth0.Outgoing), options) : helperMissing.call(depth0, "connnum", (depth0 && depth0.Outgoing), options));
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += "</span>\n			</li>\n			<li>\n				<span class=\"glyphicon glyphicon-chevron-down pull-left\"></span>\n				Entrantes\n				<span class=\"badge pull-right\">";
  options = {hash:{},data:data};
  stack2 = ((stack1 = helpers.connnum || (depth0 && depth0.connnum)),stack1 ? stack1.call(depth0, (depth0 && depth0.Incoming), options) : helperMissing.call(depth0, "connnum", (depth0 && depth0.Incoming), options));
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += "</span>\n			</li>\n		</ul>\n	</li>\n	";
  return buffer;
  }

  buffer += "<ul id=\"conn_ips\">\n	";
  stack1 = helpers.each.call(depth0, (depth0 && depth0.connections), {hash:{},inverse:self.noop,fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n</ul>";
  return buffer;
  });
})();