pragma solidity ^0.8.2;

contract ShopAgreement {
    address payable buyer;
    address payable courier=payable(address(0));
    address payable owner_of_shop;

    uint256 amount_to_be_paid;

    uint256 amount_that_is_paid=0;

    bool contract_finished=false;

    modifier not_before{
        require(amount_that_is_paid==amount_to_be_paid,"Transfer not complete.");
        _;
    }

    modifier not_after{
        require(contract_finished==false,"The contract has been closed.");
        _;
    }

    modifier check_buyer(address b){
        require((payable(b))==buyer,"Invalid customer account.");
        _;
    }


    constructor(uint amount,address bu,address own){
        buyer=payable(bu);
        amount_to_be_paid=amount;
        owner_of_shop=payable(own);
    }

    function confirm(address b) external payable not_before not_after{
       
        address payable bb=payable(b);
        require(bb==buyer,"Invalid customer account.");
        require(courier!=payable(address(0)),"Delivery not complete.");

        
        owner_of_shop.transfer(amount_that_is_paid * 4 / 5);
        courier.transfer(amount_that_is_paid / 5);

        contract_finished=true;
    }

    function pay(address b) external payable not_after{
        address payable bb=payable(b);
        require(bb==buyer,"Invalid customer account.");
        require(amount_that_is_paid!=amount_to_be_paid,"Transfer already complete.");
        amount_that_is_paid=msg.value;
        
    }

    function take_order(address cou) external payable not_before not_after{
        courier=payable(cou);
    }

}