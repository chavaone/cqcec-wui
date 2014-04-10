(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['lastconnections'] = template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  var buffer = "", stack1, stack2;
  buffer += "\n	<li id=\"conn"
    + escapeExpression(((stack1 = ((stack1 = data),stack1 == null || stack1 === false ? stack1 : stack1.index)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "\" class=\"well well-sm connection\" onclick=\"app.show_ip_last_connection_details('"
    + escapeExpression(((stack1 = ((stack1 = data),stack1 == null || stack1 === false ? stack1 : stack1.index)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "', '"
    + escapeExpression(((stack1 = (depth0 && depth0.ip_origen)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "', '"
    + escapeExpression(((stack1 = (depth0 && depth0.ip_dest)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "')\">\n		<div class=\"brief\">\n			<ul class=\"ip\">\n				<li class=\"ip_add\">"
    + escapeExpression(((stack1 = (depth0 && depth0.ip_origen)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "</li>\n				<li class=\"domain\">\n					<span class=\"domain\">\n						";
  stack2 = helpers['if'].call(depth0, (depth0 && depth0.orig_islocal), {hash:{},inverse:self.program(4, program4, data),fn:self.program(2, program2, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += "\n				</li>\n			</ul>\n			<span class=\"icon-chevron-sign-right\"></span>\n			<span class=\"proto\">"
    + escapeExpression(((stack1 = (depth0 && depth0.proto)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "</span>\n			<span class=\"icon-chevron-sign-right\"></span>\n			<ul class=\"ip\">\n				<li class=\"ip_add\">"
    + escapeExpression(((stack1 = (depth0 && depth0.ip_dest)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "</li>\n				<li class=\"domain\">\n					<span class=\"domain\">\n						";
  stack2 = helpers['if'].call(depth0, (depth0 && depth0.dest_islocal), {hash:{},inverse:self.program(9, program9, data),fn:self.program(2, program2, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += "\n				</li>\n			</ul>\n			";
  stack2 = helpers['if'].call(depth0, (depth0 && depth0.number), {hash:{},inverse:self.noop,fn:self.program(12, program12, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += "\n		</div>\n		<div class=\"more\">\n	 		<hr>\n	 		<div class=\"details\">\n				<i class=\"icon-spin icon-refresh refresh-icon\"></i>\n			</div>\n		</div>\n		</li>\n	";
  return buffer;
  }
function program2(depth0,data) {
  
  
  return "\n							(local)</span>\n						";
  }

function program4(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n							";
  stack1 = helpers['if'].call(depth0, (depth0 && depth0.domain_orig), {hash:{},inverse:self.program(7, program7, data),fn:self.program(5, program5, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n							</span>\n							<a class=\"icon-pencil edit_button\" href=\"javascript:void(0)\" onclick=\"app.edit_domain_cache('"
    + escapeExpression(((stack1 = (depth0 && depth0.ip_dest)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "', '"
    + escapeExpression(((stack1 = (depth0 && depth0.domain_orig)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "')\"></a>\n						";
  return buffer;
  }
function program5(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n								("
    + escapeExpression(((stack1 = (depth0 && depth0.domain_orig)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + ")\n							";
  return buffer;
  }

function program7(depth0,data) {
  
  
  return "\n								(unknown)\n							";
  }

function program9(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n							";
  stack1 = helpers['if'].call(depth0, (depth0 && depth0.domain_dest), {hash:{},inverse:self.program(7, program7, data),fn:self.program(10, program10, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n							</span>\n							<a class=\"icon-pencil edit_button\" href=\"javascript:void(0)\" onclick=\"app.edit_domain_cache('"
    + escapeExpression(((stack1 = (depth0 && depth0.ip_dest)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "', '"
    + escapeExpression(((stack1 = (depth0 && depth0.domain_dest)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "')\"></a>\n						";
  return buffer;
  }
function program10(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n								("
    + escapeExpression(((stack1 = (depth0 && depth0.domain_dest)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + ")\n							";
  return buffer;
  }

function program12(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n			<span class=\"badge number_badge pull-right\">"
    + escapeExpression(((stack1 = (depth0 && depth0.number)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1))
    + "</span>\n			";
  return buffer;
  }

function program14(depth0,data) {
  
  
  return "\n		<h4>Non hai conexións.</h4>\n	";
  }

  buffer += "<ul id=\"lastconnections\">\n	";
  stack1 = helpers.each.call(depth0, (depth0 && depth0.connections), {hash:{},inverse:self.program(14, program14, data),fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n </ul>";
  return buffer;
  });
})();