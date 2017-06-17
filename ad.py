#encoding:utf-8

import sys


class ADBase:
    def __init__(self, name, value, type):
        self._name = name
        self._value = value
        self._type = type
    
    def _partial(self, partial):
        pass
    
    def _expression(self):
        pass

G_STATIC_NAME_INDEX = 0
OP_ADD = "plus"
OP_MINUS = "minus"
OP_MUL = "multiply"
OP_DIV = "divide"
OP_POW = "pow"
PARTIAL_FAIL = 0
PARTIAL_OK = 1

class ADConstant(ADBase):
    def __init__(self, value):
        global G_STATIC_NAME_INDEX
        self._value = value
        self._name = 'CONTANT_'+str(G_STATIC_NAME_INDEX)
        G_STATIC_NAME_INDEX += 1
        self._type = 'CONTANT'
        self._dvalue = 0.0
    
    def _partial(self, partial):
        self._dvalue = 0.0
        return ADConstant(0)
    
    def _expression(self):
        return str(self._value)
    
    def _calc_value(self):
        return self._value

class ADVariable(ADBase):
    
    def __init__(self, name, value = None):
        self._name = name
        self._value = value
        self._type = "VARIABLE"
        self._dvalue = 0.0
    
    def _set_value(self, value):
        self._value = value
    
    def _calc_value(self):
        return self._value

    def _partial(self, partial):
        if partial._name == self._name:
            self._dvalue = 1.0
            return ADConstant(1)
        else:
            self._dvalue = 0.0
            return ADConstant(0)
    
    def _expression(self):
        return str(self._name)


class ADOperation(ADBase):
    def __init__(self, a, b, op_type):
        """
        if op_type != OP_POW:
            if a == None or b == None:
                print 'Error to Consturct ADOperation!'
                exit(1)
        else:
            if a != None and b != None:
                print 'Error to Consturct ADOperation!'
                exit(1)
        """
        self._operate_type = op_type
        self._left_variable = a
        self._right_variable = b
        self._value = 0.0
        self._dvalue = 0.0

    def _partial(self, partial):
        if partial._type != "VARIABLE":
            return None
        if self._operate_type == OP_ADD or self._operate_type == OP_MINUS:
            variable = ADOperation(self._left_variable._partial(partial), \
                self._right_variable._partial(partial), \
                self._operate_type)
            self._dvalue = self._left_variable._dvalue + self._right_variable._dvalue
            return variable
        elif self._operate_type == OP_MUL:
            variable_left = ADOperation(self._left_variable._partial(partial), \
                self._right_variable, \
                self._operate_type)
            variable_right = ADOperation(self._left_variable, \
                self._right_variable._partial(partial), \
                self._operate_type)
            self._dvalue = self._left_variable._dvalue * self._right_variable._value + \
                self._left_variable._value * self._right_variable._dvalue
            return ADOperation(variable_left, variable_right, OP_ADD)
        elif self._operate_type == OP_DIV:
            variable_a = ADOperation(self._left_variable._partial(partial), \
                self._right_variable, \
                OP_MUL)
            variable_b = ADOperation(self._left_variable, \
                self._right_variable._partial(partial), \
                OP_MUL)
            variable_c = ADOperation(variable_a, variable_b, OP_MINUS)
            variable_d = ADOperation(self._right_variable, ADConstant(2), OP_POW)
            print self._right_variable._expression(), self._right_variable._value
            self._dvalue = ((self._left_variable._dvalue * self._right_variable._value) - \
                (self._left_variable._value * self._right_variable._dvalue)) / \
                (self._right_variable._value ** 2)
            return ADOperation(variable_c, variable_d, OP_DIV)
        elif self._operate_type == OP_POW:
            c = ADConstant(self.right.value - 1)
            variable_a = ADOperation(self._left_variable, c, OP_POW)
            variable_b = ADOperation(self._right_variable, variable_a, OP_MUL)
            variable = ADOperation(self._left_variable._partial(partial), variable_b, OP_MUL)
            self._dvalue = self._right_variable._value * (self._left_variable._value ** c) * self._left_variable._dvalue

    def _calc_value(self):
        if self._operate_type == OP_ADD:
            self._value = self._left_variable._calc_value()
            self._value += self._right_variable._calc_value()

        elif self._operate_type == OP_MINUS:
            self._value = self._left_variable._calc_value() - \
                self._right_variable._calc_value()
        elif self._operate_type == OP_DIV:
            self._value = self._left_variable._calc_value() / \
               self._right_variable._calc_value()
        elif self._operate_type == OP_MUL:
            self._value = self._left_variable._calc_value() * \
               self._right_variable._calc_value()
        elif self._operate_type == OP_POW:
            self._value = self._left_variable._calc_value() ^ \
               self._right_variable._calc_value()
        return self._value


    def _expression(self):
        if self._operate_type == OP_ADD:
            return self._left_variable._expression() \
               +"+"+\
                self._right_variable._expression()
        elif self._operate_type == OP_MINUS:
            return self._left_variable._expression() \
               +"-"+\
                self._right_variable._expression()
        elif self._operate_type == OP_DIV:
            return "("+self._left_variable._expression()+")" \
               +"/" \
               +"("+self._right_variable._expression()+")"
        elif self._operate_type == OP_MUL:
            return "("+self._left_variable._expression()+")" \
               +"*" \
               +"("+self._right_variable._expression()+")"
        elif self._operate_type == OP_POW:
            return "("+self._left_variable._expression()+")" \
               +"^" \
               +"("+self._right_variable._expression()+")"


x = ADVariable("x")
y = ADVariable("y")
a = ADOperation(ADConstant(2), x, OP_MUL)
b = ADOperation(a, ADConstant(1), OP_ADD)
f = ADOperation(ADConstant(1), b, OP_DIV)


x._set_value(0.11)
# 计算数值
f._calc_value()
# 求导
f._partial(x)
print f._value
print f._dvalue
print f._expression()

x1 = ADVariable("y")

