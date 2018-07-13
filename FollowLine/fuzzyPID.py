import numpy as np
import skfuzzy.control as ctrl
def fuzzyPID(e, de):
    # Create the three fuzzy variables - two inputs, one output
    error = ctrl.Antecedent(np.linspace(-80, 80, 5), 'error')
    delta = ctrl.Antecedent(np.linspace(-160, 160, 5), 'delta')
    Kp = ctrl.Consequent(np.linspace(0.0006, 0.004, 5), 'Kp')
    Kd = ctrl.Consequent(np.linspace(0.0002, 0.0005, 5), 'Kd')
    # =============================================================================
    # Ki = ctrl.Consequent(np.arange(0,0.001, 0.0001), 'Ki')
    # =============================================================================
    
    # Here we use the convenience `automf` to populate the fuzzy variables with
    # terms. The optional kwarg `names=` lets us specify the names of our Terms.
    names = ['bn', 'sn', 'ze', 'sp', 'bp']
    error.automf(names=names)
    delta.automf(names=names)
    Kp.automf(names=names)
    Kd.automf(names=names)
    
    # =============================================================================
    # error.view()
    # delta.view()
    # Kp.view()
    # Kd.view()
    # =============================================================================
    
    # =============================================================================
    # Kp Rules
    # =============================================================================
    KpRuleBp = ctrl.Rule(antecedent=((error['bn'] & delta['bn']) |
                                     (error['sn'] & delta['bn']) |
                                     (error['bn'] & delta['sn'])),
                         consequent= Kp['bp'], label = 'rule Kp bp')
    
    KpRuleSp = ctrl.Rule(antecedent=((error['ze'] & delta['bn']) | 
                                     (error['ze'] & delta['sn']) |
                                     (error['sn'] & delta['sn']) |
                                     (error['sn'] & delta['ze']) |
                                     (error['bn'] & delta['ze']) |
                                     (error['bn'] & delta['sp'])),
                         consequent=Kp['sp'], label = 'rule Kp sp')
    
    KpRuleZe = ctrl.Rule(antecedent=((error['bp'] & delta['bn']) |
                                     (error['sp'] & delta['bn']) |
                                     (error['sp'] & delta['sn']) |
                                     (error['ze'] & delta['ze']) |
                                     (error['sn'] & delta['sp']) |
                                     (error['sn'] & delta['bp']) |
                                     (error['bn'] & delta['bp'])),
                         consequent=Kp['ze'], label = 'rule Kp ze')
    
    KpRuleSn = ctrl.Rule(antecedent=((error['bp'] & delta['sn']) |
                                     (error['bp'] & delta['ze']) |
                                     (error['sp'] & delta['ze']) |
                                     (error['sp'] & delta['sp']) |
                                     (error['ze'] & delta['sp']) |
                                     (error['ze'] & delta['bp'])),
                         consequent=Kp['sn'], label = 'rule Kp sn')
    
    KpRuleBn = ctrl.Rule(antecedent=((error['bp'] & delta['sp']) |
                                     (error['bp'] & delta['bp']) |
                                     (error['sp'] & delta['bp'])),
                         consequent=Kp['bn'], label = 'rule Kp bn')
    
    # =============================================================================
    # Kd Rules
    # =============================================================================
    KdRuleBp = ctrl.Rule(antecedent=((error['bp'] & delta['bp']) |
                                     (error['sn'] & delta['bp']) |
                                     (error['bn'] & delta['bp'])),
                         consequent=Kd['bp'], label = 'rule Kd bp')
    
    KdRuleSp = ctrl.Rule(antecedent=((error['bp'] & delta['bn']) |
                                     (error['sp'] & delta['bp']) |
                                     (error['ze'] & delta['bp']) |
                                     (error['bn'] & delta['sp'])),
                         consequent=Kd['sp'], label = 'rule Kd sp')
    
    KdRuleZe = ctrl.Rule(antecedent=((error['bp'] & delta['sn']) |
                                     (error['bp'] & delta['ze']) |
                                     (error['bp'] & delta['sp']) |
                                     (error['sp'] & delta['sp']) |
                                     (error['ze'] & delta['sp']) |
                                     (error['sn'] & delta['sp']) |
                                     (error['bn'] & delta['ze'])),
                         consequent=Kd['ze'], label = 'rule Kd ze')
    
    KdRuleSn = ctrl.Rule(antecedent=((error['sp'] & delta['bn']) |
                                     (error['sp'] & delta['sn']) |
                                     (error['sp'] & delta['ze']) |
                                     (error['ze'] & delta['sn']) |
                                     (error['ze'] & delta['ze']) |
                                     (error['sn'] & delta['bn']) |
                                     (error['sn'] & delta['sn']) |
                                     (error['sn'] & delta['ze']) |
                                     (error['bn'] & delta['sn'])),
                         consequent=Kd['sn'], label = 'rule Kd sn')
    
    KdRuleBn = ctrl.Rule(antecedent=(error['sn'] & delta['bn']),
                         consequent=Kd['bn'], label = 'rule Kd bn')
    
    # =============================================================================
    # Set up simulation
    # =============================================================================
    CtrlFuzzyPID = ctrl.ControlSystem([KpRuleBn, KpRuleBp, KpRuleSn, KpRuleSp, 
                                       KpRuleZe, KdRuleBn, KdRuleBp, KdRuleSn, 
                                       KdRuleSp, KdRuleZe])
    
    FuzzyPID = ctrl.ControlSystemSimulation(CtrlFuzzyPID)
    
    FuzzyPID.input['error'] = e
    FuzzyPID.input['delta'] = de
    
    FuzzyPID.compute()
    
    return FuzzyPID.output['Kp'], FuzzyPID.output['Kd']

